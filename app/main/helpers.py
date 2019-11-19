import random

# ======================================================== Q 1.1


def is_perm(s, t):

    if len(s) != len(t):
        return False

    counter = [0]*128

    for i in range(len(s)):
        curr_letter = ord(s[i]) - ord('A')
        counter[curr_letter] += 1

    for i in range(len(s)):
        curr_letter = ord(t[i]) - ord('A')
        counter[curr_letter] -= 1

        if counter[curr_letter] < 0:
            return False

    return True


def generate_word_search():

    words = ['potato', 'baked', 'with', 'cheese']
    max_len = 0

    for i in range(len(words)):
        words[i] = sorted(words[i], key=lambda x: random.random())
        if max_len < len(words[i]):
            max_len = len(words[i])

    charac = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'y', 'z', 'w', 'm', 'n']
    # build sample as max_len by max_len + 3 matrix
    sample = [sorted(charac[0:max_len + 3], key=lambda x: random.random()),
              sorted(charac[0:max_len + 3], key=lambda x: random.random())]
    sample_str = ''.join(sample[0]) + ';'
    sample_str += ''.join(sample[1]) + ';'

    count = 2

    for i in range(len(words)):
        curr_len = len(words[i])
        rand = random.randint(0, max_len + 3 - curr_len)

        temp = sorted(charac[0:rand], key=lambda x: random.random())
        temp += words[i]
        temp += sorted(charac[0:max_len + 3 - (rand + curr_len)], key=lambda x: random.random())
        sample.append(temp)
        sample_str += ''.join(sample[count]) + ';'
        count += 1

    sample.append(sorted(charac[0:max_len + 3], key=lambda x: random.random()))
    sample.append(sorted(charac[0:max_len + 3], key=lambda x: random.random()))
    sample_str += ''.join(sample[len(sample) - 2]) + ';'
    sample_str += ''.join(sample[len(sample) - 1]) + ';'

    return [sample, sample_str]

def word_search_handler(word, curr_data):

    sample = []
    answer = []
    found = False

    # populate sample and look for horizontal words
    for i in range(len(curr_data) - 1):
        sample.append([])
        answer.append([])

        for j in range(len(curr_data[i])):
            sample[i].append(curr_data[i][j])
            answer[i].append(0)

        for k in range(len(sample[i]) - len(word) + 1):
            if is_perm(word, ''.join(sample[i][k:len(word) + k])):
                answer[i][k:len(word) + k] = [1] * len(word)
                found = True

    num_rows = len(sample)
    num_cols = len(sample[0])

    # look for vertical words
    for i in range(num_cols):
        for j in range(num_rows):

            for k in range(num_rows - len(word) + 1):

                # build word to compare to
                temp = ''
                for m in range(k, len(word) + k):
                    temp += sample[m][i]

                if is_perm(word, temp):
                    found = True
                    for m in range(k, len(word) + k):
                        answer[m][i] = 1

    return [found, answer, sample, num_rows, num_cols]


# ============================================================================== Q 2.2


def URL_converter(str, true_len):

    num_spaces = 0
    for i in range(true_len):
        if str[i] == ' ':
            num_spaces += 1

    counter = true_len + num_spaces * 2
    if true_len < len(str):
        str[true_len] = '0'

    for i in range(true_len - 1, -1, -1):

        if str[i] == ' ':
            str[counter - 1] = '0'
            str[counter - 2] = '2'
            str[counter - 3] = '%'
            counter -= 3

        else:
            str[counter - 1] = str[i]
            counter -= 1

    return str


#==================================================================== Q 4.1


def path_exists(start, end, graph):

    if start == end:
        return True

    visited = [0] * len(graph)
    visited[start] = 1
    queue = [start]

    while len(queue) > 0:
        curr = queue[0]

        for i in range(len(graph[curr])):

            if graph[curr][i] == end:
                return True

            if not visited[graph[curr][i]]:
                visited[graph[curr][i]] = True
                queue.append(graph[curr][i])

        queue = queue[1:]

    return False


def random_edges():

    edges = ''
    edges_vec = [0] * 13
    for i in range(13):
        temp = random.randint(0, 10)

        if temp <= 5:
            edges_vec[i] = 1
            edges += '1'
        else:
            edges += '0'

    return [edges, edges_vec]


def build_graph(edges_vec):

    graph = []
    for i in range(8):
        graph.append([])

    # build graph
    for i in range(len(edges_vec)):

        if edges_vec[i] == 0:
            continue

        # i is connected to i + 1 (total 3)
        if i < 3:
            graph[i].append(i + 1)
            graph[i + 1].append(i)

        # i + 1 is connected to i + 2 (total 3)
        elif i >= 3 and i < 6:
            graph[i + 1].append(i + 2)
            graph[i + 2].append(i + 1)

        # i - 6 is connected to (i - 6) + 4 (total 4)
        elif i >= 6 and i < 10:
            graph[i - 6].append((i - 6) + 4)
            graph[(i - 6) + 4].append(i - 6)

        # i - 10 is connected to (i - 10) + 5
        else:
            graph[i - 10].append((i - 10) + 5)
            graph[(i - 10) + 5].append(i - 10)

    return graph

import boto3
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Recipes")

def getRecipe(id):


    response = table.get_item(
        Key={
            'recipe_id': str(id)
        }
    )

    return response['Item']


def writeRecipe(field_edited, val, id):

    try:
        response = table.get_item(
            Key={
                'recipe_id': str(id)
            }
        )

        new_item = response['Item']

    except KeyError:
        new_item = {'recipe_id': str(id)}
        table.put_item(
            Item={
                'recipe_id': "-1",
                'num_recipes': int(id)
            }
        )

    if field_edited == 'recipe_name':
        new_item['recipe_name'] = val
        new_item['query_name'] = val.lower()
        new_item['edited'] = 1

    elif field_edited == 'recipe_time':
        new_item['recipe_time'] = int(val)

    else:
        info = field_edited.split('-')
        field_edited = info[0]

        # indicates change in instructions
        if field_edited == 'to_be_read':
            step_changed = str(int(info[1]) + 1)

            if new_item.get('cooking_instructions', 0) == 0:
                new_item['cooking_instructions'] = {step_changed: {'to_be_read': val}}
            else:
                new_item['cooking_instructions'][step_changed] = {'to_be_read': val}

            new_item['edited'] = 1

        elif field_edited == 'recipe_ingredients':

            val_info = val.split('-')
            temp = new_item.get('recipe_ingredients', {})

            temp[val_info[0]] = {'quantity': {'count': val_info[1], 'unit': val_info[2]}}
            new_item['recipe_ingredients'] = temp

    table.put_item(
        Item=new_item
    )


def nextRecipeId():

    response = table.get_item(
        Key={
            'recipe_id': "-1"
        }
    )

    return int(response['Item']['num_recipes']) + 1




def updateRecipe(field_edited, val, id):

    response = table.get_item(
        Key={
            'recipe_id': str(id)
        }
    )

    new_item = response['Item']

    if field_edited == 'recipe_name':
        new_item['recipe_name'] = val
        new_item['query_name'] = val.lower()
        new_item['edited'] = 1

    else:
        info = field_edited.split('-')
        field_edited = info[0]

        # indicates change in instructions
        if field_edited == 'to_be_read':
            step_changed = str(int(info[1]) + 1)
            new_item['cooking_instructions'][step_changed]['to_be_read'] = val


            new_item['edited'] = 1

        elif field_edited == 'recipe_ingredients':

            val_info = val.split('-')
            temp = new_item['recipe_ingredients']

            # delete old entry
            del temp[val_info[0]]


            # make sure to delete entry that was deleted by user
            if val_info[1] != '':
                temp[val_info[1]] = {'quantity': {'count': val_info[2], 'unit': val_info[3]}}

            new_item['recipe_ingredients'] = temp

    table.put_item(
        Item=new_item
    )




