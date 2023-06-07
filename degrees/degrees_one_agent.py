import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            #print(row["id"])
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass
'''
    for id in people:
        print(f"{id}:", people[id])

    print('\n')
    for id in names:
        print(f"{id}:", names[id])
        
    print('\n')
    for id in movies:
        print(f"{id}:", movies[id])
'''


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"
    print(directory)

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    first_time = True
    while (first_time or input("\nDo you want to continue? (Y):").lower()=='y'):
        first_time = False
        
        source_id = person_id_for_name(input("\nName as full name, or last name: "))
        if source_id is None:
            #sys.exit("Person not found.")
            print("Person not fount")
            continue
        target_id = person_id_for_name(input("\nName as full name, or sir name: "))
        if target_id is None:
            #sys.exit("Person not found.")
            print("Person not fount")
            continue

        path = shortest_path(source_id, target_id)

        if path is None:
            print("Not connected.")
        else:
            degrees = len(path)
            print(f"\n{degrees} degrees of separation.")
            path = [(None, source_id)] + path
            for i in range(degrees):
                person1 = people[path[i][1]]["name"]
                person2 = people[path[i + 1][1]]["name"]
                movie = movies[path[i + 1][0]]["title"]
                print(f"{i + 1}: {person1} and {person2} starred in {movie}")

def shortest_path(source_id, target_id):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # Implemented below the search method using Queue Frontier
    # raise NotImplementedError

    name = ""
    if(not len(people[source_id]['movies'])):
        name = people[source_id]['name']+' has'
    if(not len(people[target_id]['movies'])):
        if name:
            name = "Both Persons have"
        else:
            name = people[target_id]['name']+' has'
    if name:
        print(f"\n{name} not acted in any movie")
        return None

    nodes_checked = []
    path_to_target=[]
    node_for_check = Node(source_id, None, None)

    frontier = QueueFrontier()
    frontier_node_count = 1
    node_target_in_frontier = False
    print("\nPlease wait, while searching for the connections...")
    while True:

        nodes_checked.append(node_for_check)

        #Summerise the path if the target node is found
        if(node_for_check.state==target_id):
            parent_id=node_for_check.state
            for node in reversed(nodes_checked):
                if(node.state==parent_id and node.parent is not None):
                    path_to_target += [(node.action,node.state)]
                    parent_id=node.parent
            path_to_target.reverse()
            break

        #If the goal/target node is not the frontier, expand the current node
        if not node_target_in_frontier:
            neighbours = neighbors_for_person(node_for_check.state)
            #Update the frontier with the connected nodes for the current node
            for neighbour in neighbours:
                if(not(frontier.contains_state(neighbour[1])) and\
                    not(any(node.state==neighbour[1] for node in nodes_checked))):
                    node = Node(neighbour[1],node_for_check.state,neighbour[0])
                    frontier.add(node)
                    frontier_node_count += 1 #for checking & optimization purpose
                    if node.state == target_id:
                        node_target_in_frontier = True
                        break
        
        #List the new frontier for testing
        #frontier.list_state_of_loaded_nodes()
        try:
            node_for_check = frontier.remove()
        except Exception:
            #return None
            break
    
    print("Total checked IDs:", len(nodes_checked))
    print("Total nodes added to the Frontier:", frontier_node_count)
    print("connected nodes:")
    print(path_to_target)
    return path_to_target

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """    
    person_ids = list(names.get(name.lower(), set()))
    person_ids += person_ids_for_part_entry(name)
    if len(person_ids) == 0:
        return None

    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]

def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors

def person_ids_for_part_entry(name_entered):
    """
    Returns the person ids for entry of first name or sir name.
    """
    person_ids = []

    if len(name_entered) == 0:
        return person_ids

    name_entered = name_entered.lower()
    for name in names:
        name_splitted = name.split()
        if name_entered == name_splitted[-1]:
            name_list = list(names.get(name))
            for person_id in name_list:
                person_ids.append(person_id)
    
    return person_ids

if __name__ == "__main__":
    main()
