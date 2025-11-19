import random
import numpy as np


def generate_random_sequence_2cond(condition1, condition2, length, balance_factor=0.5):

    '''
    # Example usage:
    condition1 = "A"
    condition2 = "B"
    sequence_length = 10
    balance_factor = 0.5  # Adjust this value to control the balance

    random_sequence = generate_random_sequence(condition1, condition2, sequence_length, balance_factor)
    '''

    sequence = []
    current_condition = random.choice([condition1, condition2])

    for _ in range(length):
        sequence.append(current_condition)

        # Introduce some randomness to change conditions
        if random.random() < balance_factor:
            current_condition = condition1 if current_condition == condition2 else condition2

    # check balancing
    idx_cond1 = [index for index, value in enumerate(sequence) if value == condition1]
    count1 = 0
    count2 = 0
    for idx in idx_cond1:
        if idx + 1 < len(sequence):
            if sequence[idx+1] == condition1:
                count1 += 1
            else:
                count2 += 1

    print('Balancing check')
    print('Condition1 count: ', cond1_frequency)
    print('Condition2 count: ', cond2_frequency)
    print(f'Number of times that the condition1 is followed by condition1: {count1}')
    print(f'Number of times that the condition1 is followed by condition2: {count2}')

    return sequence

def generate_random_sequence_2cond_maxCons(condition1, condition2, length, balance_factor=0.5, max_consecutive=2, order_balance=2):

    '''
    # Example usage:
    condition1 = "A"
    condition2 = "B"
    sequence_length = 20
    balance_factor = 0.5  # Adjust this value to control the balance
    max_consecutive = 3
    order_balance=2

    random_sequence = generate_random_sequence(condition1, condition2, sequence_length, balance_factor, max_consecutive)

    I put max consecutive 2 to have min condition frequency > 0.01
    order_balance define the allowed maximum difference between the number of times that cond1 follows cond2 and vice versa 
    '''


    # check also that the two conditions appear with the same frequency
    cond1_frequency = 1
    cond2_frequency = -1
    balanced = False

    while cond1_frequency != cond2_frequency or not balanced: # regenerate the sequence

        sequence = []
        current_condition = random.choice([condition1, condition2])
        consecutive_count = 1

        for _ in range(length):
            sequence.append(current_condition)

            # Introduce randomness to change conditions with balanced frequency
            if random.random() < balance_factor and consecutive_count < max_consecutive:
                current_condition = condition1 if current_condition == condition1 else condition2
                consecutive_count += 1
            else:
                current_condition = condition1 if current_condition == condition2 else condition2
                consecutive_count = 1
        idx_cond1 = [index for index, value in enumerate(sequence) if value == condition1]
        idx_cond2 = [index for index, value in enumerate(sequence) if value == condition2]

        cond1_frequency = len(idx_cond1)
        cond2_frequency = len(idx_cond2)

        # check balancing
        count1 = 0
        count2 = 0
        for idx in idx_cond1:
            if idx + 1 < len(sequence):
                if sequence[idx + 1] == condition1:
                    count1 += 1
                else:
                    count2 += 1

        balanced = (abs(count1-count2)<=order_balance)


    print('Balance check')   
    print('Condition1 count: ', cond1_frequency)
    print('Condition2 count: ', cond2_frequency)
    print(f'Number of times that the condition1 is followed by condition1: {count1}')
    print(f'Number of times that the condition1 is followed by condition2: {count2}')

    return sequence

def shuffle_without_consecutive_duplicates_old(arr):

    while True:
        shuffled_arr = arr.copy()
        random.shuffle(shuffled_arr)

        # check  if any consecutive elements are the same emotion
        if all(x.split('_')[0] != y.split('_')[0] for x, y in zip(shuffled_arr, shuffled_arr[1:])):
            return shuffled_arr

def shuffle_without_consecutive_duplicates(arr):

    n = len(arr)
    while True:
        # create a list of indices and shuffle them
        indices = list(range(n))
        random.shuffle(indices)

        # apply the shuffled indices to arr
        shuffled_arr = [arr[i] for i in indices]

        # check condition
        if all(x.split('_')[0] != y.split('_')[0]
               for x, y in zip(shuffled_arr, shuffled_arr[1:])):
            return shuffled_arr, indices


