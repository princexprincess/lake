import random
import math
import sys

class FrozenLake(object):

    def __init__(self, width, height, start, targets, blocked, holes):
        self.initial_state = start 
        self.width = width
        self.height = height
        self.targets = targets
        self.holes = holes
        self.blocked = blocked

        self.actions = ('n', 's', 'e', 'w')
        self.states = set()
        for x in range(width):
            for y in range(height):
                if (x,y) not in self.targets and (x,y) not in self.holes and (x,y) not in self.blocked:
                    self.states.add((x,y))

        # Parameters for the simulation
        self.gamma = 0.9
        self.success_prob = 0.8
        self.hole_reward = -5.0
        self.target_reward = 1.0
        self.living_reward = -0.1

    #### Internal functions for running policies ###

    def get_transitions(self, state, action):
        """
        Return a list of (successor, probability) pairs that
        can result from taking action from state
        """
        result = []
        x,y = state
        remain_p = 0.0

        if action=="n":
            success = (x,y-1)
            fail = [(x+1,y), (x-1,y)]
        elif action=="s":
            success =  (x,y+1)
            fail = [(x+1,y), (x-1,y)]
        elif action=="e":
            success = (x+1,y)
            fail= [(x,y-1), (x,y+1)]
        elif action=="w":
            success = (x-1,y)
            fail= [(x,y-1), (x,y+1)]
          
        if success[0] < 0 or success[0] > self.width-1 or \
           success[1] < 0 or success[1] > self.height-1 or \
           success in self.blocked: 
                remain_p += self.success_prob
        else: 
            result.append((success, self.success_prob))
        
        for i,j in fail:
            if i < 0 or i > self.width-1 or \
               j < 0 or j > self.height-1 or \
               (i,j) in self.blocked: 
                    remain_p += (1-self.success_prob)/2
            else: 
                result.append(((i,j), (1-self.success_prob)/2))
           
        if remain_p > 0.0: 
            result.append(((x,y), remain_p))
        return result

    def move(self, state, action):
        """
        Return the state that results from taking this action
        """
        transitions = self.get_transitions(state, action)
        new_state = random.choices([i[0] for i in transitions], weights=[i[1] for i in transitions])
        return new_state[0]

    def simple_policy_rollout(self, policy):
        """
        Return (Boolean indicating success of trial, total rewards) pair
        """
        state = self.initial_state
        rewards = 0
        while True:
            if state in self.targets:
                return (True, rewards+self.target_reward)
            if state in self.holes:
                return (False, rewards+self.hole_reward)
            state = self.move(state, policy[state])
            rewards += self.living_reward

    def QValue_to_value(self, Qvalues):
        """
        Given a dictionary of q-values corresponding to (state, action) pairs,
        return a dictionary of optimal values for each state
        """
        values = {}
        for state in self.states:
            values[state] = -float("inf")
            for action in self.actions:
                values[state] = max(values[state], Qvalues[(state, action)])
        return values


    #### Some useful functions for you to visualize and test your MDP algorithms ###

    def test_policy(self, policy, t=500):
        """
        Following the policy t times, return (Rate of success, average total rewards)
        """
        numSuccess = 0.0
        totalRewards = 0.0
        for i in range(t):
            result = self.simple_policy_rollout(policy)
            if result[0]:
                numSuccess += 1
            totalRewards += result[1]
        return (numSuccess/t, totalRewards/t)

    def get_random_policy(self):
        """
        Generate a random policy.
        """
        policy = {}
        for i in range(self.width):
            for j in range(self.height):
                policy[(i,j)] = random.choice(self.actions)
        return policy

    # def gen_rand_set(self, width, height, size):
    #     """
    #     Generate a random set of grid spaces.
    #     Useful for creating randomized maps.
    #     """
    #     mySet = set([])
    #     while len(mySet) < size:
    #         mySet.add((random.randint(0, width), random.randint(0, height)))
    #     return mySet

    def print_map(self, policy=None):
        """
        Print out a map of the frozen pond, where * indicates start state,
        T indicates target states, # indicates blocked states, and O indicates holes.
        A policy may optimally be provided, which will be printed out on the map as well.
        """
        sys.stdout.write(" ")
        for i in range(2*self.width):
            sys.stdout.write("--")
        sys.stdout.write("\n")
        for j in range(self.height):
            sys.stdout.write("|")
            for i in range(self.width):
                if (i, j) in self.targets:
                    sys.stdout.write("T\t")
                elif (i, j) in self.holes:
                    sys.stdout.write("O\t")
                elif (i, j) in self.blocked:
                    sys.stdout.write("#\t")
                else:
                    if policy and (i, j) in policy:
                        a = policy[(i, j)]
                        if a == "n":
                            sys.stdout.write("^")
                        elif a == "s":
                            sys.stdout.write("v")
                        elif a == "e":
                            sys.stdout.write(">")
                        elif a == "w":
                            sys.stdout.write("<")
                        sys.stdout.write("\t")
                    elif (i, j) == self.initial_state:
                        sys.stdout.write("*\t")
                    else:
                        sys.stdout.write(".\t")
            sys.stdout.write("|")
            sys.stdout.write("\n")
        sys.stdout.write(" ")
        for i in range(2*self.width):
            sys.stdout.write("--")
        sys.stdout.write("\n")

    def print_values(self, values):
        """
        Given a dictionary {state: value}, print out the values on a grid
        """
        for j in range(self.height):
            for i in range(self.width):
                if (i, j) in self.holes:
                    value = self.hole_reward
                elif (i, j) in self.targets:
                    value = self.target_reward
                elif (i, j) in self.blocked:
                    value = 0.0
                else:
                    value = values[(i, j)]
                print("%10.2f" % value, end='')
            print()


    #### Your code starts here ###

    def value_iteration(self, threshold=0.001):
        """
        The value iteration algorithm to iteratively compute an optimal
        value function for all states.
        """
        values = dict((state, 0.0) for state in self.states)
        ### YOUR CODE HERE ###
        thresh = 1
        while thresh:
            thresh = 0
            values_temp = {}
            for state in self.states:
                V_is = []
                for action in self.actions:
                    transitions = self.get_transitions(state,action)
                    V_i = 0
                    for new_state, prob in transitions:
                        if new_state in self.targets:
                            V_i += prob * (self.living_reward + self.gamma * self.target_reward)
                        elif new_state in self.holes:
                            V_i += prob * (self.living_reward + self.gamma * self.hole_reward)
                        else:
                            V_i += prob * (self.living_reward + self.gamma * values[new_state])
                    V_is.append(V_i)
                V_i = max(V_is)
                values_temp[state] = V_i
            for state in self.states:
                if abs(values[state] - values_temp[state]) > threshold:
                    thresh = 1
            values = values_temp
        return values

    def extract_policy(self, values):
        """
        Given state values, return the best policy.
        """
        policy = {}
        ### YOUR CODE HERE ###
        for state in self.states:
            pols = []
            for action in self.actions:
                transitions = self.get_transitions(state,action)
                val = 0
                for new_state, prob in transitions:
                    if new_state in self.targets:
                        val += prob * (self.living_reward + self.gamma * self.target_reward)
                    elif new_state in self.holes:
                        val += prob * (self.living_reward + self.gamma * self.hole_reward)
                    else:
                        val += prob * (self.living_reward + self.gamma * values[new_state])
                pols.append((val,action))
            opt = max(pols)
            policy[state] = opt[1]
        return policy


    def Qlearner(self, alpha, epsilon, num_robots):
        """
        Implement Q-learning with the alpha and epsilon parameters provided.
        Runs number of episodes equal to num_robots.
        """
        Qvalues = {}
        for state in self.states:
            for action in self.actions:
                Qvalues[(state, action)] = 0

        ### YOUR CODE HERE ###
        for i in range(num_robots):
            robot_pos = (0,0)
            while True:
                choice = random.choices(['random','policy'], weights=[epsilon,1-epsilon])
                if choice == 'random':
                    action = random.choices(self.actions)
                    robot_pos_new = self.move(robot_pos,action)
                else:
                    opt = max([(Qvalues[(robot_pos,action)],action) for action in self.actions])
                    action = opt[1]
                    robot_pos_new = self.move(robot_pos,action)
                if robot_pos_new in self.targets:
                    sample = self.living_reward + self.gamma * self.target_reward
                elif robot_pos_new in self.holes:
                    sample = self.living_reward + self.gamma * self.hole_reward
                else:
                    opt = max([(Qvalues[(robot_pos_new,action)],action) for action in self.actions])
                    sample = self.living_reward + self.gamma * Qvalues[(robot_pos_new,opt[1])]
                Qvalues[(robot_pos,action)] = (1-alpha)*Qvalues[(robot_pos,action)] + alpha * sample
                if robot_pos_new in self.targets or robot_pos_new in self.holes:
                    break
                else:
                    robot_pos = robot_pos_new
        return Qvalues

    def Qlearner_mark_II(self, alpha, epsilon, num_robots):
        Qvalues = {}
        for state in self.states:
            for action in self.actions:
                Qvalues[(state, action)] = 0
        for i in range(num_robots):
            robot_pos = (0,0)
            while True:
                k = 3
                epsilon = 1/math.log(k)
                alpha = 1/math.log(k)
                choice = random.choices(['random','policy'], weights=[epsilon,1-epsilon])
                if choice == 'random':
                    action = random.choices(self.actions)
                    robot_pos_new = self.move(robot_pos,action)
                else:
                    opt = max([(Qvalues[(robot_pos,action)],action) for action in self.actions])
                    action = opt[1]
                    robot_pos_new = self.move(robot_pos,action)
                if robot_pos_new in self.targets:
                    sample = self.living_reward + self.gamma * self.target_reward
                elif robot_pos_new in self.holes:
                    sample = self.living_reward + self.gamma * self.hole_reward
                else:
                    opt = max([(Qvalues[(robot_pos_new,action)],action) for action in self.actions])
                    sample = self.living_reward + self.gamma * Qvalues[(robot_pos_new,opt[1])]
                Qvalues[(robot_pos,action)] = (1-alpha)*Qvalues[(robot_pos,action)] + alpha * sample
                k += 1
                if robot_pos_new in self.targets or robot_pos_new in self.holes:
                    break
                else:
                    robot_pos = robot_pos_new
        return Qvalues

if __name__ == "__main__":
   
    # Create a lake simulation
    width = 8
    height = 8
    start = (0,0)
    targets = set([(3,4)])
    blocked = set([(3,3), (2,3), (2,4)])
    holes = set([(4, 0), (4, 1), (3, 0), (3, 1), (6, 4), (6, 5), (0, 7), (0, 6), (1, 7)])
    lake = FrozenLake(width, height, start, targets, blocked, holes)

    # rand_policy = lake.get_random_policy()
    # lake.print_map()
    # lake.print_map(rand_policy)
    # print(lake.test_policy(rand_policy))

    # part 1
    print('#################### Part 1 ####################')
    opt_values = lake.value_iteration()
    lake.print_values(opt_values)
    print()

    # part 2
    print('#################### Part 2 ####################')
    opt_policy = lake.extract_policy(opt_values)
    lake.print_map(opt_policy)
    print(lake.test_policy(opt_policy))
    print()
    
    # part 3
    print('#################### Part 3 ####################')
    Qvalues = lake.Qlearner(alpha=0.5, epsilon=0.5, num_robots=50)
    learned_values = lake.QValue_to_value(Qvalues)
    learned_policy = lake.extract_policy(learned_values)
    lake.print_map(learned_policy)
    print(lake.test_policy(learned_policy), 'with 50 robots') # more robot (e.g. 1000 robots) may not get better TOTAL REWARD according to my tests.
    print()

# part 4
    print('#################### Part 4 ####################')
    # generate a random new map is not quite simple, targets and holes and obstacles could overlap
    Qvalues = lake.Qlearner_mark_II(alpha=0.5, epsilon=0.5, num_robots=50) # use a decreasing epsilon = 1/math.log(k) and alpha = 1/math.log(k)
    learned_values = lake.QValue_to_value(Qvalues)
    learned_policy = lake.extract_policy(learned_values)
    lake.print_map(learned_policy)
    print(lake.test_policy(learned_policy), 'with 50 robots') # seems sliiiiiightly better than constant parameters
    print()