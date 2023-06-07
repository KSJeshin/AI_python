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
        
        source_id = person_id_for_name(input("\nName as full name, or first name, or sir name: "))
        if source_id is None:
            #sys.exit("Person not found.")
            print("Person not fount")
            continue
        target_id = person_id_for_name(input("\nName as full name, or first name, or sir name: "))
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
    
    path=[]
    source_nodes_checked = []
    target_nodes_checked = []
    source_node_to_check = Node(source_id, None, None)
    target_node_to_check = Node(target_id, None, None)

    frontier_source = QueueFrontier()
    frontier_target = QueueFrontier()
    print("\nPlease wait, while searching for the connections...")

    path_found = False
    while True: #(input("Continue:").lower()=='y'):

        source_nodes_checked.append(source_node_to_check)
        #print("\tChecking Node from source",source_node_to_check.state)
        target_nodes_checked.append(target_node_to_check)
        #print("\n\tChecking Node from target",target_node_to_check.state)

        if(len(frontier_source.frontier)>=len(frontier_target.frontier)):
            for node in target_nodes_checked:
                print("Target stock checked", node.state, node.parent)
                if(source_node_to_check.state == node.state):
                    path_found = True
                    print("\nIntersection found by source in target")
                    node_id = source_node_to_check.state
                    for node in reversed(source_nodes_checked):
                        if(node.state==node_id and node.parent is not None):
                            path += [(node.action,node.state)]
                            node_id=node.parent
                            print(node.state, node.parent, node.action)
                    path.reverse()
                    print("\n")

                    node_id = source_node_to_check.state
                    for node in reversed(target_nodes_checked):
                        if(node.state==node_id and node.parent is not None): 
                            path += [(node.action,node.parent)]
                            print(node.state, node.parent, node.action)
                            node_id=node.parent

                if path_found:
                    break
        
        print("\n")
        if (len(frontier_source.frontier)<len(frontier_target.frontier)): #not path_found:
            for node in source_nodes_checked:
                print("Source stock checked", node.state, node.parent)
                if(target_node_to_check.state == node.state):
                    path_found = True
                    print("\nIntersection found by target in source")
                    node_id=target_node_to_check.state
                    for node in reversed(source_nodes_checked):
                        if(node.state==node_id and node.parent is not None):
                            path += [(node.action,node.state)]
                            node_id=node.parent
                            print(node.state, node.parent, node.action)
                    path.reverse()
                    print("\n")

                    node_id = target_node_to_check.state
                    for node in reversed(target_nodes_checked):
                        if(node.state==node_id and node.parent is not None):
                            path += [(node.action,node.parent)]
                            print(node.state, node.parent, node.action)
                            node_id=node.parent

                if path_found:
                    break


        #To break outside the while loop
        if path_found:
            print("full path:",path)
            break

        #Identify the connected nodes for source_id
        neighbours = neighbors_for_person(source_node_to_check.state)
        #Expand the source frontier with the connected nodes to the current node
        for neighbour in neighbours:
            if(not(frontier_source.contains_state(neighbour[1])) and\
                not(any(node.state==neighbour[1] for node in source_nodes_checked))):
                node = Node(neighbour[1],source_node_to_check.state,neighbour[0])
                frontier_source.add(node)
        
        #Identify the connected nodes for target_id
        neighbours = neighbors_for_person(target_node_to_check.state)
        #Expand the target frontier with the connected nodes to the current node
        for neighbour in neighbours:
            if(not(frontier_target.contains_state(neighbour[1])) and\
                not(any(node.state==neighbour[1] for node in target_nodes_checked))):
                node = Node(neighbour[1],target_node_to_check.state,neighbour[0])
                frontier_target.add(node)


        #List the new frontiers for testing
        #print("\nSource Frontier:")
        #frontier_source.list_state_of_loaded_nodes()

        #print("\nTarget Frontier:")
        #frontier_target.list_state_of_loaded_nodes()

        try:
            source_node_to_check = frontier_source.remove()
            target_node_to_check = frontier_target.remove()
        except Exception:
            return None
    
    print("Total Nodes checked", len(source_nodes_checked)+len(target_nodes_checked))
    return path

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """    
    person_ids = list(names.get(name.lower(), set()))
    #person_ids += person_ids_for_part_entry(name)
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
