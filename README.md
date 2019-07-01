# Timetable Generator
Timetable generator for university schedule implemented in Python using *genetic algorithms*.

### Abstract
This project implements one of possible solutions for generating university schedule. 
The proposed solution is based on methods of evolutionary computing, uses *(1+1) evolutionary strategy* and *simulated hardening*. 
The success of solution is estimated on fulfillment of given constraints and criteria. 
Results of testing the algorithm show that all hard constraints are satisfied, while additional criteria are optimized to a certain extent.

### Problem 
The assignment is to find generic solution that will facilitate generating schedule for university (this specific problem is adjusted to `Faculty of Computing in Belgrade`). 

Each class on faculty is represented as block (lasts arbitrary number of hours, mostly form 1 to 4). 
For conducting every class required are: *teacher*, *classroom*, *start time*, *duration* and *groups* which attend the class. It is also know in advance which groups attend which class and all classrooms are the same size (each group can fit to a classroom). 
<br />Teaching is done on faculty from 9AM until 9PM on each work day. 

**Input data** for each class are *teachers’ name*, *subject*, *type*, *duration* and list of *allowed classrooms*. 
<br />**Output data** are classroom and time for each class. Time is determined by day (Monday to Friday) and start hour of the class.

### Constraints

1. Resources can not overlap timewise
    - No teacher can hold two classes at the same time
    - No group can listen for two classes at the same time
    - No classroom can receive two classes at the same time
    > Note: under the term "same time" is not meant only at the beginning of the class, it should be taken into account the duration of the class. 
          If the resource is busy at the moment `T1` and the class lasts `t1`, then the resource can only be re-occupied at the moment `T2 = T1 + t1`.
2. Class should take place in one of the allowed classrooms
3. If the subject has several forms of teaching, the preferred order for each group is the *lectures*, *exercises*, and *laboratory exercises*.

Constraints `1` and `2` must be met, while the `3rd` limit is "soft" and allowed to be violated. 
<br />Additional criteria for estimating solution (used also for cost function):
  * Fulfill hard constraints (1 & 2)
  * Fulfill soft constraints (3)
  * Minimize total "idle" for each group (eliminating pause between classes)
  * Minimize total "idle time" for each teacher (elimination of pause between classes)
  * Provide one hour on a teaching week where no one has classes

### Solution

The algorithm for the timetable is represented as table with its columns as classrooms and rows allowed times for classes, while the elements of the table are the specific class held in proper classroom and given time. 
Table is a matrix with dimensions 60 x number of classrooms, where 60 corresponds to total number of possible times during the week (5 workdays, 12 hours a day). 

Element of matrix can be empty if there is no teaching held in given time and classroom or it can contain appropriate class index. 
<br />Index of the class is determined by: *teachers’ name*, *subject*, *type* (lectures, exercises or laboratory exercises), *duration*, *allowed classrooms* and *groups*. 
Because of different duration of classes, the same indexes appear in the table multiple times and are always in vertical blocks (they take consecutive fields in the same column). 

The representation of the schedule is on the following picture.

<a href="url"><img src="https://github.com/NDresevic/timetable-generator/blob/master/matrix%20schedule.png" height="600"></a>

Basic idea of this approach is simplicity in changing terms and classrooms by just changing the block in the matrix taken by the class. 
Schedule matrix allows that one of the hard constraints is always satisfied, while calculating the cost is easily computed. 
Because of the way of placing classes in matrix it is ensured that at most one class is at one classroom at any given time, the algorithm will never put a class in non-empty field. 

Also, the checkout if the class is in the proper classroom is just examining if the class can be in that column. 
Overlaps of teachers and groups are examined by checking the rest of the classes which are in the same row. 
Soft constraint and additional criteria, such as idle for groups are calculated based on additional structures in linear time.

Besides general idea to solving the problem, for optimisation and fulfillment of constraints the two methods of evolutionary computing are used, *(1+1) evolutionary strategy* and *simulated hardening*.

### Algorithm

The algorithm consists of the following steps:
1. **Loading and processing data**
  <br />The classes are loaded from the JSON file and are allocated to the appropriate structures. 
  Also, random data mixing is done.
2. **Model setting**
  <br />Creation of schedule matrix and dictionaries representing empty fields, filled fields in a matrix, order of classes for each type of class and group, an empty group idle, and an empty teacher's idle.
3. **Generating the initial population**
  <br />Classes are arranged in vertically consecutive blank spaces of the matrix so that they are in the appropriate classroom.
4. **(1 + 1) evolution strategy for hard constraints**
  <br />The selection of classes that change the place in the schedule is based on the cost of the classes calculating only the hard constraints. Classes with the highest cost are chosen and with a certain probability mutated. Mutation is changing the field in the matrix by looking for a free field that meets all the rigid constraints. Schwefel's notation is also used.
5. **Simulated hardening for additional criteria**
  <br />Optimizes the previously generated schedule by minimizing the idle time for groups for all days and the existence of free hour in which there is no teaching. In each iteration, a random number of classes are mututed, i.e. they change the place in the matrix so they continue to meet hard constraints. For the cooling schedule, a geometric temperature drop is used.
6. **Representing schedule and statistics**

### Testing & Results
The algorithm was tested on 3 different schedules (`input1.txt`, `input2.txt`, `input3.txt`) and for each ran 10 times. 

Class allocation is first performed by an evolutionary algorithm, where the sigma parameter takes the value `2`, the number of runs `5`, while the maximum stagnation is `200`. 
After that, the schedule is optimized by the simulated hardening algorithm where the initial temperature is `0.5`, and the number of iterations is `2500`.

The results of all runs are shown in `Table 1`. Also, for each input file, one schedule has been selected and detailed statistics is shown in `Table 2`. 
This schedule was selected based on the lowest average idle time for groups and professors, subjected to the availability of existence of free hour in the week.

|               | *input1.txt*  | *input2.txt*  | *input3.txt*  |
| ------------- | ------------- | ------------- | ------------- |
| Fulfillment of hard constraints  | 100% | 100%  | 100%  |
| Fulfillment of soft constraints  | 58.42%  | 44.56% | 47.52% |
| Average idle for groups <br />(all days together)| 2.43 | 3.35 | 4.27|
| Average idle for teachers <br />(all days together)| 0.22 | 1.04 | 1.22|
| Existance of free hour  | 100% | 100%  | 100%  |

***Table 1:** Statistics obtained by average of 10 test runs.*<br />
<br />

|               | *input1.txt*  | *input2.txt*  | *input3.txt*  |
| ------------- | ------------- | ------------- | ------------- |
| Fulfillment of hard constraints  | 100% | 100%  | 100%  |
| Fulfillment of soft constraints  | 51.58%  | 51.02% | 46.11% |
| Maximum idle for groups <br />(in one day) | 4 | 6 | 6|
| Total idle for groups <br />(all days together)| 31 | 145 | 184 |
| Average idle for groups <br />(all days together)| 1.29 | 3.30 | 4.18|
| Maximum idle for teachers <br />(in one day) | 7 | 6 | 8|
| Total idle for teachers <br />(all days together)| 17 | 64 | 110 |
| Average idle for teachers <br />(all days together)| 0.45 | 1.03 | 1.75|
| Free hour | Friday 9AM | Thursday 8PM  | Friday 8PM |

***Table 2:** Statistics of best schedules out of 10 test runs.*

### Use
Running `scheduler.py` runs the code executing the algorithm for the data that is loaded from the file whose path is in the `main` function in the same file.

