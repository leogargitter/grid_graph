# grid_graph

For running this project I recomment using a virtual env. In your env:

```
pip install requirements.txt
```

To generate the grid and graph, run the main file:

```
python3 main.py <int>width <int>height
```

The grid will be generated in file named "grid.png" and the graph on the "grid_graph.png".


I don't recommend running with a grid wich is bigger than 80x80, the time complexity of the function _create_edges_between_buildings_and_roads of GridGraph is really bad, I will try to make it usable until 11/02 EOD.