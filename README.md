# MazeBacktracking
UPE Fall 2018 Coding Challenge

#### Setup:

To run the progam, run:

```$ python maze.py```

#### Implementation:

The program makes a POST request to http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com to receive a token. Using the token, I make GET request to obtain information about the maze (size, current location, status, levels completed, and total levels). To move through the maze, I make a POST request using the token, specifying the direction I want to move in, which returns whether the action resulted in a successful move, a wall hit, an out-of-bounds error, or the end of the maze. 
