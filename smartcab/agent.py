import random
import operator
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def buildQ(self):
        Q = {}
        action_set = {None: 0, 'forward': 0, 'left': 0, 'right': 0}
        light_states = ['red', 'green']
        lrfn = ['left', 'right', 'forward', None]
        oncoming_states = lrfn
        left_states = lrfn
        right_states = lrfn
        waypoint_states = lrfn
        for val in light_states:
            light = val
            for val in oncoming_states:
                oncoming = val
                for val in left_states:
                    left = val
                    for val in right_states:
                        right = val
                        for val in waypoint_states:
                            waypoint = val
                            Q[str((('light', light), ('oncoming', oncoming),
                                ('right', right), ('left', left), ('waypoint', waypoint)))] = action_set
        return Q

    def setQVal(self, state, action, val):
        return []

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.Q = self.buildQ()
        self.gamma = .8
        self.prev = {'state': None, 'action': None, 'reward': None}

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

       	action_choices = (None, 'forward', 'left', 'right')
        action = self.next_waypoint

        state = str((('light', inputs['light']), ('oncoming', inputs['oncoming']),
            ('right', inputs['right']), ('left', inputs['left']), ('waypoint', self.next_waypoint)))

        # set of Q values for all actions from current state
        q_actions = self.Q[state]
        # action with max q value
        action = max(q_actions.iteritems(), key=operator.itemgetter(1))[0]

        if self.prev['state'] != None:
            # max Q(s',a')
            q_action_max = q_actions[action]
            q_prev = self.prev['reward'] + (self.gamma * q_action_max)
            self.Q[self.prev['state']][self.prev['action']] = q_prev

        # Execute action and get reward
        reward = self.env.act(self, action)
        self.prev['reward'] = reward
        self.prev['state'] = state
        self.prev['action'] = action

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=4, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
