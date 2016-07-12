import random
import operator
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def addQState(self, state):
        self.Q[state] = {None: 0, 'forward': 0, 'left': 0, 'right': 0}
        return self.Q[state]

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.Q = {}
        self.alpha = .5
        self.gamma = .3
        self.epsilon = .1 # avoid local maxima
        self.prev = {'state': None, 'action': None, 'reward': None}
        self.state = None

    def reset(self, destination=None):
        self.planner.route_to(destination)

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

       	action_choices = (None, 'forward', 'left', 'right')
        action = self.next_waypoint

        """
        we don't use deadline here as it greatly increases dimensionality.
        dimensionality aside, its not very useful to us since we dont know how
        far from the destination we are at any point in time.
        """
        self.state = str((('light', inputs['light']), ('oncoming', inputs['oncoming']),
            ('right', inputs['right']), ('left', inputs['left']), ('waypoint', self.next_waypoint)))

        if self.state in self.Q:
            q_actions = self.Q[self.state]
        else:
            q_actions = self.addQState(self.state)

        """
        use epsilon greedy here where epsilon is .1. that is, if a random draw
        on U[0,1] < epsilon, take a random action. otherwise, use the action
        with highest Q value
        """
        if random.random() < self.epsilon:
            action_roll = random.randint(0, 3)
            action = q_actions.keys()[action_roll]
        else:
            action = max(q_actions.iteritems(), key=operator.itemgetter(1))[0]


        """
        since we don't really have a transition function in this instance, we
        cannot directly determine which state each of our possible actions will
        take us to. to get around this, we keep track of what the previous reward,
        state, and action were and then update the Q value for the previous
        sttate action pair when we arrive at the new state, s'.
        """
        if self.prev['state'] != None:
            # max Q(s',a')
            q_action_max = q_actions[action]
            # Q(s,a) <- (1 - a) * Q(s,a) + a * (r + gamma * max_a'(Q(s', a')))
            q_prev = ((1 - self.alpha) * self.Q[self.prev['state']][self.prev['action']]) + \
                (self.alpha * (self.prev['reward'] + (self.gamma * q_action_max)))
            self.Q[self.prev['state']][self.prev['action']] = q_prev

        # Execute action and get reward
        reward = self.env.act(self, action)
        self.prev['reward'] = reward
        self.prev['state'] = self.state
        self.prev['action'] = action

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=2, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
