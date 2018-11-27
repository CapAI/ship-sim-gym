import random
import unittest

from pymunk import Vec2d

from ship_gym.game import ShipGame
from ship_gym.ship_env import ShipEnv, DEFAULT_STATE_VAL


class TestShipEnv(unittest.TestCase):

    def setUp(self):
        self.game = ShipGame(speed=1, fps=100, bounds=(300,300))
        self.env = ShipEnv(self.game, history_size=2, n_ship_track=3)
        self.env.reset()

    def test_reset(self):

        # Test default player position
        self.env.reset()

        self.assertTrue(self.game.player.x, self.game.DEFAULT_SPAWN_POINT.x)
        self.assertTrue(self.game.player.y, self.game.DEFAULT_SPAWN_POINT.y)

        self.game.add_goal(400, 400)
        for _ in range(3):
            self.env.step(self.env.action_space.sample()) # take a random action

        p = Vec2d(300, 212)
        self.game.reset(spawn_point=p)
        self.assertTrue(self.game.player.x, p.x)
        self.assertTrue(self.game.player.y, p.y)

    def test_done(self):
        self.game.add_goal(100, 100)
        self.assertFalse(self.env.is_done())

        self.game.reset(spawn_point=Vec2d(100, 100))
        self.env.step(4) # Should spawn on top of the new goal

        self.assertTrue(self.env.is_done())

        self.game.reset(spawn_point=Vec2d(100, 100))
        self.game.add_goal(200, 200)
        self.env.step(4)  # Should spawn on top of the new goal
        self.assertFalse(self.env.is_done())

    def test_action(self):
        start_pos = Vec2d(10, 40)
        self.game.reset(spawn_point=start_pos)
        self.game.add_goal(100, 100)

        player = self.game.player

        # Forward, backward, right, left, nothing
        for _ in range(10):
            self.env.step(4) # Do nothing
            self.assertEqual(player.x, start_pos.x)
            self.assertEqual(player.y, start_pos.y)

        for i in range(10):
            self.env.step(0)  # Forward

            if i > 0:
                self.assertGreater(player.y, start_pos.y)
                self.assertAlmostEqual(player.x, start_pos.x)

        self.game.reset(spawn_point=start_pos)
        self.game.add_goal(100, 100)
        player = self.game.player
        for _ in range(10):
            self.env.step(3)
            self.assertEqual(player.x, start_pos.x)
            self.assertEqual(player.y, start_pos.y)

            print(player.x, player.y)
            print(player.force_vector)

        for i in range(10):
            self.env.step(0)  # Forward

            print("Forward move, pos : ", (player.x , player.y))
            if i > 3:
                self.assertGreater(player.y, start_pos.y)
                self.assertGreater(player.x, start_pos.x)


        # Testing moving towards the right
        self.game.reset(spawn_point=start_pos)
        self.game.add_goal(100, 100)
        player = self.game.player
        for _ in range(10):
            self.env.step(2)
            self.assertEqual(player.x, start_pos.x)
            self.assertEqual(player.y, start_pos.y)

        for i in range(10):
            self.env.step(0)  # Forward

            print("Forward move, pos : ", (player.x, player.y))
            if i > 3:
                self.assertGreater(player.y, start_pos.y)
                self.assertLess(player.x, start_pos.x)


    def test_history_states(self):

        p = Vec2d(32, 84)

        self.env.reset(spawn_point=p)
        self.game.add_goal(32, 100)
        player = self.game.player

        last_state = None

        for _ in range(10):
            last_p_x = player.x
            last_p_y = player.y
            states, _, _, _ = self.env.step(0)

            print("states = ", states)
            print("last = ", last_p_x, last_p_y)

            print(self.game.player.x)
            print("current = ", player.x, player.y)

            self.assertListEqual(list(states[:2]), [last_p_x, last_p_y])

            # if last_state:
            #     self.assertListEqual(list(states[self.env]), )

            # last_state = states[len(states) / self.env.history_size:]

            # self.(stat)
            # self.assertEqual(states[self.env.n_states:self.env.n_states+2], [player.x, player.y])


    def test_goal_states(self):

        p = Vec2d(10, 20)

        game = ShipGame(fps=100, speed=10, bounds=[1000, 900])
        env = ShipEnv(game, n_ship_track=0, history_size=1)
        env.reset(spawn_point=p)

        g = game.add_goal(10, 100)

        for _ in range(10):
            states, _, _, _ = env.step(4)  # Do nothing
            self.assertListEqual(list(states[2:4]), [g.x, g.y])

        # No matter how many goals you add farther away this one should be the closest goal
        for _ in range(10):
            game.add_goal(10 + random.randint(100, 200), 100 + random.randint(100, 200))
            states, _, _, _ = env.step(4)  # Do nothing
            self.assertListEqual(list(states[2:4]), [g.x, g.y])

        # Let's start over
        game = ShipGame(fps=100, speed=1, bounds=[400, 800])
        env = ShipEnv(game, n_ship_track=0, history_size=1)

        base_x = game.bounds[0] / 2
        env.reset(spawn_point=[base_x, 1])

        # g0 = game.add_goal(base_x, -20)
        g1 = game.add_goal(base_x - 100, 10)
        g2 = game.add_goal(base_x + 101, 10)

        g3 = game.add_goal(base_x, 120)
        g4 = game.add_goal(base_x, 160)

        print(game.goals)

        # g1 will be the closest until player exceeds y=20
        while len(game.goals) == 4:
            states, _, _, _ = env.step(0)  # Forward

            print("GOALS LEFT=")
            print(game.goals)
            print("STATES=")
            print(states)

            if game.player.y > 20:  # New closest goal!
                self.assertListEqual(list(states[2:4]), [g3.x, g3.y])
                break
            else:
                self.assertListEqual(list(states[2:4]), [g1.x, g1.y])

        while len(game.goals) == 3:
            states, _, _, _ = env.step(0)  # Forward

            print("GOALS LEFT=")
            print(game.goals)
            print("STATES=")
            print(states)

            self.assertListEqual(list(states[2:4]), [g4.x, g4.y])

        states, _, _, _ = env.step(0)  # Forward
        self.assertListEqual(list(states[2:4]), [g1.x, g1.y])

        g2.x = game.player.x + 25
        g2.y = game.player.y + 25
        states, _, _, _ = env.step(4)  # Forward
        self.assertListEqual(list(states[2:4]), [g2.x, g2.y])


    def test_reward(self):
        # Let's start over
        game = ShipGame(fps=100, speed=1, bounds=[400, 800])
        env = ShipEnv(game, n_ship_track=0, history_size=1)

        self.game.add_goal(1000, 1000)



