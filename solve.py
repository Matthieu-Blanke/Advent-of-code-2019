from maze import Maze

data_path = 'input/input.txt'
maze = Maze(data_path)

print (f'x0 = {maze.x0}, y0 = {maze.y0}')
print (f'x_max = {maze.x_max}, y_max = {maze.y_max}')

print('Preprocessing the maze')
deletions = 0
for i in range(200):
    count = maze.simplify()
    # print(f'count = {count}')
    deletions += count
print(f'deletions = {deletions}')
# print(f'map = {maze.map}')


# keys = ('a', 'c')
# distance = maze.shortest_path(*keys)
# distance_bi = maze.shortest_path(*keys)
# print(f'distance = {distance}')

print('Searching shortest path')
distance = maze.run('@')
print(f'solution = {distance}')
