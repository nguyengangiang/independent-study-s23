# independent-study-s23
Develop a function to generalize goals from scrape file and observe the result of the function as well as filter out results that do not match the correct output.
Overview of goal generalization function
The generalization function takes in a goal and returns a list of different generalized versions of the goal. We did that by replacing the variables by different variables and parsing the operator and generalized the result of the operation. For example, the goal ‘x+y’, will output [‘(x+y)', ‘x0’]. For now, the generalization function only handles mathematical operations and function calls.

Goal filtering function

Objective
Take any goal from the scrape file, parse it and return False if not generalizable and the generalized version if it could be generalized. 

Implementation
I first looked through the goals in the scrape file and identified cases that our generalization function did not handle, such cases are: 
When goal contains if-else statement
When goal contains come Coq grammar such as :=, |, =>
After identifying such cases, now I simply parse the scrape goal and check if it contains any of the aforementioned syntax.
If it passed the syntax test, I called the generalization function on the goal and evaluate the result
