from django.utils import timezone
from off.elements.services import elements
from off.perceptions.services import element_data_shapers
from django.conf import settings
from collections import namedtuple

DataTuple = namedtuple('DataTuple', ['perception', 'data'])


class PerceptionDataFlyweightFactory:
    _flies = dict()

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def get_perception_data(self, element, shape):
        return self.__get_and_register_data__(element, shape).perception

    def get_data(self, element, shape, user):
        return self.__get_and_register_data__(element, shape).data

    def __get_and_register_data__(self, element, shape, user):
        data = self._flies.get(element.uid, None)
        if not data:
            data = self.__create_data__(element, shape)
        elif data.data_checksum != element.data_checksum:
            data.update(self.__shape_element_data__(element, shape))
        return data

    def get_data_from_uid(self, uid, default=None):
        return self._flies.get(uid, default).data

    def get_perception_data_from_uid(self, uid, default=None):
        return self._flies.get(uid, default).data

    def __create_data__(self, element, shape):
        data = self.__shape_element_data__(element, shape)
        return DataTuple(PerceptionData(element.uid, element.data_checksum, shape), data)

    def __shape_element_data__(self, element, shape):
        shaper = element_data_shapers.get_shapers(shape.value)[0]
        return shaper.get_obj(element.data)


class PerceptionData:
    def __init__(self, uid, data_checksum, shape, **kwargs):
        self.data_checksum = data_checksum
        self.uid = uid
        self.shape = shape
        self.startpoint_for_data = set()  # the data connected from this data
        self.endpoint_for_data = set()  # the data connected to this data
        self.last_update = timezone.now()
        self.last_time_perceived = timezone.now()
        self.clusters = set()  # the available data clusters
        self.data_clusters = dict()  # the clusters per connected data

    def add_data(self, data: PerceptionData, through_cluster: PerceptionData = None):
        if through_cluster:
            if data.uid not in self.data_clusters:
                self.data_clusters[data.uid] = set()
            self.data_clusters[data.uid].add(through_cluster)
            self.clusters.add(through_cluster)
            through_cluster.add_data(data)
        self._interconnect_data(self, self, data)

    def fill_limited_data(self, depth, uids, filter_clusters, exclude_clusters):
        if uids is None or not isinstance(uids, dict):
            raise ValueError('uids must be a dict()')
        if depth <= 0:
            return
        uids[self.uid] = self
        for cluster in [c for c in self.clusters if self.__allows_cluster__(c)]:
            cluster.fill_limited_data(depth - 1, uids, filter_clusters, exclude_clusters)
        for data in [d for d in self.startpoint_for_data if d.uid not in uids]:
            data.fill_limited_data(depth - 1, uids, filter_clusters, exclude_clusters)

    def __allows_cluster__(self, cluster, walked_uids, filter_clusters, exclude_clusters):
        if cluster.uid in walked_uids:
            return False
        if filter_clusters and cluster.uid in filter_clusters:
            return True
        if not exclude_clusters or cluster.uid not in exclude_clusters:
            return True
        return False

    @property
    def has_data_connexions(self):
        return bool(self.startpoint_for_data or self.endpoint_for_data)

    def update(self, data):
        self.data = data
        self.last_update = timezone.now()

    def _interconnect_data(self, data_from, data_to):
        data_to.endpoint_for_data.add(data_from)
        data_from.startpoint_for_data.add(data_to)

    def remove_data(self, data):
        self.startpoint_for_data.discard(data)
        self.endpoint_for_data.discard(data)

        cluster = self.data_clusters.pop(data.uid, None)
        if cluster and not cluster.has_data_connexions():
            self.clusters.discard(cluster)

    def dispose(self):
        for data in self.startpoint_for_data:
            data.remove_data(self)
        for data in self.endpoint_for_data:
            data.remove_data(self)
        self.clusters.clear()
        for cluster in self.data_clusters:
            cluster.remove_data(self)
        self.data_clusters.clear()


class PerceptionDataGraph:
    no_update = (set(), set())
    """
    Perception graphs represent a point of view on the data.
    It works with a focus point and a depth attribute, allowing certain
    amount of element that can be 'perceived'.
    It works as a memory cursor, scanning the data net.
    """
    def __init__(self, *args, **kwargs):
        self._focus = None
        self._depth = getattr(settings, 'PERCEPTION_DEPTH', 3)
        self.last_update = None
        self.uids = dict()
        self._filter_clusters = None
        self._exclude_clusters = None

    def focus(self, perception_data: PerceptionData):
        """
        Sets the perception DataGraph ```focus``` to the given
        ```PerceptionData```.

        Returns a tuple (new_data, discarded_data) in focus according to depth.
        """
        if self._focus and self._focus.uid == perception_data.uid:
            return self.no_update

        self._focus = perception_data
        return self.update()

    def __update_graph__(self):
        old_uids = self.uids
        self.uids = self.__get_accessible_data__()
        self.keys = set(self.uids.keys())
        old_keys = set(old_uids.keys())
        discarded_data = old_keys.difference(self.keys)
        new_data = self.keys.difference(old_keys)
        old_uids.clear()
        old_keys.clear()
        self.last_update = timezone.now()
        return (new_data, discarded_data)

    def __get_accessible_data__(self):
        new_uids = dict()
        return self._focus.fill_limited_data(self._depth, new_uids, self._filter_clusters, self._exclude_clusters)

    def clear_filters_and_exclude(self):
        self._exclude_clusters = None
        self._filter_clusters = None
        return self.__update_graph__()

    def filter_clusters(self, clusters_uids):
        """
        Returns a tuple (new_data, discarded_data) in focus according to filtered clusters.
        """
        if self._filter_clusters == clusters_uids:
            return self.no_update
        self._filter_clusters = clusters_uids
        self._exclude_clusters = None
        return self.update()

    def exclude_clusters(self, clusters_uids):
        """
        Returns a tuple (new_data, discarded_data) in focus according to excluded clusters.
        """
        if self._exclude_clusters == clusters_uids:
            return self.no_update
        self._exclude_clusters = clusters_uids
        self._filter_clusters = None
        return self.update()

    def add_data(self, data, data_cluster, uid=None):
        """
        Adds clustered data to a ```PerceptionData``` object.

        If ```uid``` is ```None```, the ```self._focus``` is used.

        If no ```self._focus``` has been set and ```uid``` is ```None```,
        the method raises ```ValueError```
        """
        if not uid and not self._focus:
            raise ValueError('no data focus or uid provided')
        if not isinstance(data, list, set, tuple):
            data = set(data)
        if uid:
            root = self.uids.get(uid, None)
            if not root:
                raise KeyError('uid not loaded, load it first')
        else:
            root = self._focus
        for d in data:
            root.add_data(data, data_cluster)
            self.uids[data.uid] = data
        self.uids[data_cluster.uid] = data_cluster
        return self

    def get_data(self):
        """
        Gets the data according to the ```focus``` and ```depth```.

        Returns a ```tuple``` (focus_data, copy of perceived_data_dict```(uid : data)```)
        """
        if self._focus:
            return (self._focus, self.uids.copy())
        raise ValueError('focus is not set')

    def update(self):
        """
        Returns a tuple (new_data, discarded_data) according to the state of the graph
        """
        return self.__update_graph__()
