
# Off
- [Off](#Off)
  - [Data Net](#Data-Net)
  - [Data User](#Data-User)
  - [Data Distribution](#Data-Distribution)
  - [Data Consistency](#Data-Consistency)
  - [Data Focus](#Data-Focus)
  - [Data Perception](#Data-Perception)
  - [Data Cluster](#Data-Cluster)
  - [Data Browsing](#Data-Browsing)
  - [Data Search](#Data-Search)
  - [Data Access](#Data-Access)
  - [Data Encryption](#Data-Encryption)
  - [Data Apps](#Data-Apps)
  - [Data Storage](#Data-Storage)
- [Basic semantics](#Basic-semantics)

## Data Net
Let's enforce the singularity of the data.

Space is limited to the resources that we have, thus space management must be done in a sustainable way.
The current state of the art in computer science does not take that into consideration.

* One data MUST be stored only once,
* The data is always connected to the source,
* The connection between two data is data by itself, thus can be connected to other data.
* Connexions have a direction (from data1, to data2)
  * Another connection is needed to connect data2 to data1
* Data access should be constant in time

> TODO
> Do we, and if yes how to, store previous state of the data ?


## Data User
* The data user must be able to create complex data queries
  * complex means rich in terms of semantics
* The data user is represented as data itself
  * For convenience the user data is strongly linked to a User represented as a specific object (i.e not ```data```) in the database. This would allow reusing the existing auth systems.

## Data Distribution
When accessing data, the system will give a graph of accessible data to the data user.
The data value can be fetch from multiple sources.
Indeed once a data has been fetch from the mainframe to a single user, two sources for this data exist.
The mainframe act as a data tracker giving on request the available sources from which this data can be found.

## Data Consistency
Because of data distribution, the data must enforce consistency, to avoid data tampering or corruption.
* The data connections are given by the mainframe thus enforce the consistency by itself.
* The data by itself is checksumed using a sha256 algorithm.
* The data graph gives the checksum of the data to ensure consistency.

## Data Focus
* A data user can have focuses (plural) on the data net
* The focus is giving the ```point of view``` on the data that is wanted by the data user
* Data focus is a specific data (or a n-tuple of data ?)

## Data Perception
* The data user focus on the data is the root of the data perception:
  * The data user do not need to have access to the whole data at one time
  * The data user need to have access to all the connected data
  * The data user need to always have the connection to the source for each data.
* The data user perception is based on the focused data. The presented data graph will be generated according to the focused data place and to the wanted depth of perception.
  * The bigger the depth, the more data will be transmitted to the data user, leading to strong resources consumption

## Data Cluster
When 2 data are connected, the data connection can have multiple connections to other data.
The data cluster is defined as a data connected to the data connection between 2 data.

Ex (1) :
* ```data(1) : source```
* ```data(2) : doberman```
* ```connection(1) : data(1) -> data(2)```
* ```data(3) : connection(1)```
* ```data(4) : dog```
* ```connection(2) : connection(1) -> data(4)```
* ```data(5) : black```
* ```connection(3) : connection(1) -> data(5)```

```data(4):dog```
> The doberman is in the dog cluster when the perception is focused on the source.

```data(5):black```
> The doberman is in the black cluster when the perception is focused on the source

```data(2)``` clusters => ```[data(4):dog, data(5):black]```

Every data can be considered as a data cluster.

## Data Browsing

* The data user is able to browse the data connection and browse wherever it is wanted.
* The browsing is based on the user data focuses.
* The connection to the source is always accessible, providing access to the data clusters that the user data focus has through the connection to the source. This allows to enlarge the vision from the focus (data jumps).
* Through the data perception, data clusters are available
* When data clusters are selected as focus points they provide access to every data that have all those clusters specified within their connection

## Data Search

Data search is the main basis and the most interesting access point to the data.

1. The search produces results according to the searched data clusters

   This will leave the data value inspection very low. Indeed it is generally not needed, as the data user would probably prefer to narrow the results using the data clusters.
   Ex using Ex(1) : "black dogs"

## Data Access

This section concerns the access rights to the data.
When a data user creates data, the created data is connected to the user.

This data connection is connected to a ```creates``` semantic data allowing the system to understand the nature of the connection between the user or the data.
Such data users have full control on the created data (read/write).

To give access to data, a data user needs to shares it with other data. This ```shares``` semantic data is connected to the data connection between the data user that shares the data and the shared data. Then this ```shares``` data connection is connected to the data that can have access.
The ```shares``` semantic data gives **read access** only.

Allowing writing will need a ```allows_write``` semantic data connection with the same specificity as the ```shares```.

When accessing data, those connection MUST be checked to ensure a complete secure storage of the data, granting a high level of privacy.

Data without the ```creates``` semantic are considered public


## Data Encryption
For security and privacy reasons, the data net must provide a way to store encrypted data as long as encryption keys.
> TODO

## Data Apps
Apps can easily be build within the system, enjoying powerfull infrastrucure, helpers and system calls.

They will be responsible to show the final user the perception of the data that they are designed to provide.

The data apps will be summoned through the data and their semantic connections to the source or to other data.

This allows a very high ability to change the data view system.

## Data Storage
It remains very important to keep in mind that the data net efficiency will entierly rely on an accurate data definition.

By design, the data net can rearrange itself quite easily if needed.

The data apps will have to behave in a very strict manner to allow such accuracy while storing the data.

# Basic semantics
* Dictionary
* Synonyms dictionary
* Words
  * Nouns
  * Pronouns
  * Verbs
  * Determinants
  * Adjectives
  * Adverbs
  * Conjunctions
  * Prepositions
  * Ponctuations
  * Interjections
