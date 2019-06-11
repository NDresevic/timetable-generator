def subjects_order_cost(subjects_order):
    """
    Calculates percentage of soft constraints - order of subjects (P, V, L).
    :param subjects_order: dictionary where key = (name of the subject, index of the group), value = [int, int, int]
    where ints represent start times (row in matrix) for types of classes P, V and L respectively. If start time is -1
    it means that that subject does not have that type of class.
    :return: percentage of satisfied constraints
    """
    # number of subjects not in right order
    cost = 0
    # number of all orders of subjects
    total = 0

    for (subject, group_index), times in subjects_order.items():

        if times[0] != -1 and times[1] != -1:
            total += 1
            # P after V
            if times[0] > times[1]:
                cost += 1

        if times[0] != -1 and times[2] != -1:
            total += 1
            # P after L
            if times[0] > times[2]:
                cost += 1

        if times[1] != -1 and times[2] != -1:
            total += 1
            # V after L
            if times[1] > times[2]:
                cost += 1

    # print(cost, total)
    return 100 * (total - cost) / total


def empty_space_groups_cost(groups_empty_space):
    """
    Calculates total empty space of all groups for week, maximum empty space in day and average empty space for whole
    week per group.
    :param groups_empty_space: dictionary where key = group index, values = list of rows where it is in
    :return: total cost, maximum per day, average cost
    """
    # total empty space of all groups for the whole week
    cost = 0
    # max empty space in one day for some group
    max_empty = 0

    for group_index, times in groups_empty_space.items():
        times.sort()
        # empty space for each day for current group
        empty_per_day = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        for i in range(1, len(times) - 1):
            a = times[i-1]
            b = times[i]
            diff = b - a
            # classes are in the same day if their time div 12 is the same
            if a // 12 == b // 12 and diff > 1:
                empty_per_day[a // 12] += diff - 1
                cost += diff - 1

        # compare current max with empty spaces per day for current group
        for key, value in empty_per_day.items():
            if max_empty < value:
                max_empty = value

    return cost, max_empty, cost / len(groups_empty_space)


def empty_space_teachers_cost(teachers_empty_space):
    """
    Calculates total empty space of all teachers for week, maximum empty space in day and average empty space for whole
    week per teacher.
    :param teachers_empty_space: dictionary where key = name of the teacher, values = list of rows where it is in
    :return: total cost, maximum per day, average cost
    """
    # total empty space of all teachers for the whole week
    cost = 0
    # max empty space in one day for some teacher
    max_empty = 0

    for teacher_name, times in teachers_empty_space.items():
        times.sort()
        # empty space for each day for current teacher
        empty_per_day = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}

        for i in range(1, len(times) - 1):
            a = times[i - 1]
            b = times[i]
            diff = b - a
            # classes are in the same day if their time div 12 is the same
            if a // 12 == b // 12 and diff > 1:
                empty_per_day[a // 12] += diff - 1
                cost += diff - 1

        # compare current max with empty spaces per day for current teacher
        for key, value in empty_per_day.items():
            if max_empty < value:
                max_empty = value

    return cost, max_empty, cost / len(teachers_empty_space)


def free_hour(matrix):
    """
    Checks if there is an hour without classes. If so, returns it in format 'day: hour', otherwise -1.
    """
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    for i in range(len(matrix)):
        exists = True
        for j in range(len(matrix[i])):
            field = matrix[i][j]
            if field is not None:
                exists = False

        if exists:
            return '{}: {}'.format(days[i // 12], hours[i % 12])

    return -1


def hard_constraints_cost(matrix, data):
    """
    Calculates total cost of hard constraints: in every classroom is at most one class at a time, every class is in one
    of his possible classrooms, every teacher holds at most one class at a time and every group attends at most one
    class at a time.
    For everything that does not satisfy these constraints, one is added to the cost.
    :return: total cost, cost per class, cost of teachers, cost of classrooms, cost of groups
    """
    # cost_class: dictionary where key = index of a class, value = total cost of that class
    cost_class = {}
    for c in data.classes:
        cost_class[c] = 0

    cost_classrooms = 0
    cost_teacher = 0
    cost_group = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            field = matrix[i][j]                                        # for every field in matrix
            if field is not None:
                c1 = data.classes[field]                                # take class from that field

                # calculate loss for classroom
                if j not in c1.classrooms:
                    cost_classrooms += 1
                    cost_class[field] += 1

                for k in range(j + 1, len(matrix[i])):                  # go through the end of row
                    next_field = matrix[i][k]
                    if next_field is not None:
                        c2 = data.classes[next_field]                   # take class of that field

                        # calculate loss for teachers
                        if c1.teacher == c2.teacher:
                            cost_teacher += 1
                            cost_class[field] += 1

                        # calculate loss for groups
                        g1 = c1.groups
                        g2 = c2.groups
                        for g in g1:
                            if g in g2:
                                cost_group += 1
                                cost_class[field] += 1

    total_cost = cost_teacher + cost_classrooms + cost_group
    return total_cost, cost_class, cost_teacher, cost_classrooms, cost_group


def check_hard_constraints(matrix, data):
    """
    Checks if all hard constraints are satisfied, returns number of overlaps with classes, classrooms, teachers and
    groups.
    """
    overlaps = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            field = matrix[i][j]                                    # for every field in matrix
            if field is not None:
                c1 = data.classes[field]                            # take class from that field

                # calculate loss for classroom
                if j not in c1.classrooms:
                    overlaps += 1

                for k in range(len(matrix[i])):                     # go through the end of row
                    if k != j:
                        next_field = matrix[i][k]
                        if next_field is not None:
                            c2 = data.classes[next_field]           # take class of that field

                            # calculate loss for teachers
                            if c1.teacher == c2.teacher:
                                overlaps += 1

                            # calculate loss for groups
                            g1 = c1.groups
                            g2 = c2.groups
                            # print(g1, g2)
                            for g in g1:
                                if g in g2:
                                    overlaps += 1

    return overlaps
