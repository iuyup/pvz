"""Headless regression tests for the core PvZ gameplay loop."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

import pvz


class GameLogicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))
        cls.original_load_images = pvz.Game._load_images
        cls.original_load_animations = pvz.Game._load_animations
        pvz.Game._load_images = lambda self: {}
        pvz.Game._load_animations = lambda self: {}

    @classmethod
    def tearDownClass(cls):
        pvz.Game._load_images = cls.original_load_images
        pvz.Game._load_animations = cls.original_load_animations
        pygame.quit()

    def make_game(self, difficulty="normal"):
        game = pvz.Game()
        game.start_game(difficulty)
        return game

    def test_first_wave_starts_when_countdown_finishes(self):
        game = self.make_game()

        game._update_playing(pvz.START_COUNTDOWN_DURATION)

        self.assertEqual(game.wave_manager.current_wave, 1)
        self.assertTrue(game.wave_manager.in_wave)
        self.assertEqual(game.wave_manager.zombies_spawned, 1)
        self.assertEqual(len(game.zombies), 1)

    def test_viewport_scales_and_maps_mouse_coordinates(self):
        viewport = pvz.get_game_viewport((1600, 900))

        self.assertEqual(viewport.size, (1467, 900))
        self.assertEqual(pvz.window_to_game_pos(viewport.topleft, viewport), (0, 0))
        self.assertEqual(
            pvz.window_to_game_pos((viewport.right - 1, viewport.bottom - 1), viewport),
            (pvz.SCREEN_W - 1, pvz.SCREEN_H - 1),
        )
        self.assertIsNone(pvz.window_to_game_pos((viewport.x - 1, viewport.y), viewport))

    def test_zombie_only_blocks_on_contacted_forward_plant(self):
        game = self.make_game()
        game.grid[2][3] = pvz.Wallnut(2, 3)
        game.grid[2][7] = pvz.Wallnut(2, 7)
        zombie = pvz.Zombie(2, speed=0)

        zombie.x = 400
        self.assertIsNone(game.get_zombie_blocker(2, zombie.x, zombie.width))

        zombie.x = 300
        self.assertIs(game.get_zombie_blocker(2, zombie.x, zombie.width), game.grid[2][3])

    def test_pea_hits_frontmost_overlapping_zombie_not_list_order(self):
        game = self.make_game()
        game.start_countdown_timer = 999
        rear_zombie = pvz.Zombie(0, speed=0)
        front_zombie = pvz.Zombie(0, speed=0)
        rear_zombie.x = 500
        front_zombie.x = 470
        game.zombies = [rear_zombie, front_zombie]
        game.peas = [pvz.Pea(0, 480, pvz.PEA_DAMAGE)]

        game._update_playing(0)

        self.assertEqual(front_zombie.hp, pvz.ZOMBIE_HP - pvz.PEA_DAMAGE)
        self.assertEqual(rear_zombie.hp, pvz.ZOMBIE_HP)
        self.assertFalse(game.peas)

    def test_mower_kill_is_removed_and_counted(self):
        game = self.make_game()
        game.start_countdown_timer = 999
        zombie = pvz.Zombie(3, speed=0)
        zombie.x = 70
        game.zombies = [zombie]

        game._update_playing(1 / 30)
        game._update_playing(1 / 30)

        self.assertFalse(game.zombies)
        self.assertEqual(game.kills, 1)

    def test_zombie_crossing_left_edge_loses_game(self):
        game = self.make_game()
        game.start_countdown_timer = 999
        zombie = pvz.Zombie(1, speed=20)
        zombie.x = -zombie.width + 1
        game.zombies = [zombie]

        game._update_playing(0.1)

        self.assertEqual(game.state, pvz.STATE_LOSE)

    def test_final_wave_wins_only_after_last_zombie_is_gone(self):
        game = self.make_game()
        manager = game.wave_manager
        manager.current_wave = pvz.TOTAL_WAVES
        manager.in_wave = True
        manager.zombies_in_wave = 1
        manager.zombies_spawned = 1
        game.zombies = [pvz.Zombie(0, speed=0)]

        manager.try_spawn(0, game)
        self.assertEqual(game.state, pvz.STATE_PLAYING)
        self.assertFalse(manager.all_done)

        game.zombies.clear()
        manager.try_spawn(0, game)

        self.assertEqual(game.state, pvz.STATE_WIN)
        self.assertTrue(manager.all_done)

    def test_sun_click_increases_resources(self):
        game = self.make_game()
        game.add_sun(200, 200, pvz.SUN_VALUE)
        sun = game.suns[0]

        handled = game.handle_click(200, 200)

        self.assertTrue(handled)
        self.assertTrue(sun.dead)
        self.assertEqual(game.sun_count, pvz.SUN_INITIAL + pvz.SUN_VALUE)

    def test_all_difficulties_complete_expected_wave_counts(self):
        for difficulty, config in pvz.DIFFICULTY_CONFIG.items():
            with self.subTest(difficulty=difficulty):
                game = self.make_game(difficulty)
                game.start_countdown_timer = 0.0
                game._update_playing(0.0)
                spawned_total = 0

                while game.state == pvz.STATE_PLAYING:
                    manager = game.wave_manager
                    spawned_total += manager.zombies_in_wave
                    while manager.zombies_spawned < manager.zombies_in_wave:
                        manager.try_spawn(manager._spawn_interval(), game)
                    game.zombies.clear()
                    manager.try_spawn(0.0, game)
                    if game.state != pvz.STATE_PLAYING:
                        break
                    manager.try_spawn(manager._wave_cooldown(game), game)

                expected_total = sum(
                    max(
                        1,
                        int(
                            round(
                                (pvz.ZOMBIES_PER_WAVE_BASE + (wave - 1) * pvz.ZOMBIES_PER_WAVE_INC)
                                * config["zombie_count_multiplier"]
                            )
                        ),
                    )
                    for wave in range(1, pvz.TOTAL_WAVES + 1)
                )
                self.assertEqual(game.state, pvz.STATE_WIN)
                self.assertEqual(spawned_total, expected_total)

    def test_animation_manifest_loads_expected_sequences(self):
        loader = object.__new__(pvz.Game)
        loader.images = type(self).original_load_images(loader)
        animations = type(self).original_load_animations(loader)
        loader.animations = animations

        self.assertEqual(len(animations["peashooter"]["shoot"]["frames"]), 4)
        self.assertEqual(len(animations["zombie"]["walk"]["frames"]), 4)
        self.assertEqual(len(animations["zombie"]["bite"]["frames"]), 3)
        self.assertIn("produce", animations["sunflower"])
        self.assertIn("hit", animations["wallnut"])
        self.assertIn("warn", animations["cherry_bomb"])
        self.assertTrue(animations["cherry_bomb"]["warn"]["loop"])
        self.assertIsInstance(
            loader._animation_image("peashooter", "shoot", 0.15), pygame.Surface
        )

    def test_animation_frames_keep_consistent_size_and_bottom_anchor(self):
        loader = object.__new__(pvz.Game)
        loader.images = type(self).original_load_images(loader)
        animations = type(self).original_load_animations(loader)

        for asset_key, sequences in animations.items():
            frames = [
                frame["image"]
                for state, sequence in sequences.items()
                if not (asset_key == "cherry_bomb" and state == "explode")
                for frame in sequence["frames"]
            ]
            with self.subTest(asset_key=asset_key):
                sizes = {image.get_size() for image in frames}
                bounds = [image.get_bounding_rect(min_alpha=32) for image in frames]
                visible_heights = [bound.height for bound in bounds]
                bottom_offsets = [image.get_height() - bound.bottom for image, bound in zip(frames, bounds)]

                self.assertEqual(len(sizes), 1)
                self.assertLessEqual(max(visible_heights) - min(visible_heights), 1)
                self.assertLessEqual(max(bottom_offsets) - min(bottom_offsets), 1)

    def test_animation_events_preserve_existing_gameplay_timing(self):
        def sequence(loop):
            return {
                "loop": loop,
                "duration": 0.1,
                "frames": [{"duration": 0.1, "image": pygame.Surface((1, 1), pygame.SRCALPHA)}],
            }

        game = self.make_game()
        game.start_countdown_timer = 999
        game.animations = {
            "peashooter": {"idle": sequence(True), "shoot": sequence(False)},
            "sunflower": {"idle": sequence(True), "produce": sequence(False)},
            "wallnut": {"idle": sequence(True), "hit": sequence(False)},
            "cherry_bomb": {"idle": sequence(True), "warn": sequence(False), "explode": sequence(False)},
            "zombie": {"walk": sequence(True), "bite": sequence(True)},
        }

        peashooter = pvz.Peashooter(0, 1)
        peashooter.shoot_timer = pvz.PEASHOOTER_INTERVAL
        game.grid[0][1] = peashooter
        target = pvz.Zombie(0, speed=0)
        target.x = 500
        game.zombies = [target]

        game._update_playing(0)

        self.assertEqual(len(game.peas), 1)
        self.assertEqual(peashooter.animation_state, "shoot")
        game._advance_animation(peashooter, 0.1)
        self.assertEqual(peashooter.animation_state, "idle")

        sunflower = pvz.Sunflower(1, 1)
        sunflower.sun_timer = pvz.SUNFLOWER_INTERVAL
        game.grid[1][1] = sunflower
        game._update_playing(0)
        self.assertEqual(sunflower.animation_state, "produce")
        game._advance_animation(sunflower, 0.1)
        self.assertEqual(sunflower.animation_state, "idle")

        wallnut = pvz.Wallnut(0, 3)
        game.grid[0][3] = wallnut
        wallnut.take_damage(1)
        self.assertEqual(wallnut.hp, pvz.HP_WALLNUT - 1)
        self.assertEqual(wallnut.animation_state, "hit")

        target.x = 300
        target.update(0, game)
        self.assertEqual(target.animation_state, "bite")

        cherry_bomb = pvz.CherryBomb(4, 8)
        cherry_bomb.update(pvz.CHERRY_BOMB_IDLE_TIME, game)
        self.assertEqual(cherry_bomb.animation_state, "warn")
        cherry_bomb.update(pvz.CHERRY_BOMB_WARNING_TIME, game)
        self.assertEqual(cherry_bomb.animation_state, "explode")

    def test_ground_shadow_sizes_and_entity_draw_paths(self):
        self.assertEqual(pvz.PLANT_GROUND_SHADOW.get_size(), (58, 12))
        self.assertEqual(pvz.SUNFLOWER_GROUND_SHADOW.get_size(), (46, 10))
        self.assertEqual(pvz.ZOMBIE_GROUND_SHADOW.get_size(), (39, 8))

        screen = pygame.Surface((pvz.SCREEN_W, pvz.SCREEN_H))
        transparent_image = pygame.Surface((1, 1), pygame.SRCALPHA)
        calls = []
        original_draw_ground_shadow = pvz.draw_ground_shadow
        pvz.draw_ground_shadow = lambda surface, center_x, ground_y, shadow: calls.append(
            (center_x, ground_y, shadow.get_size())
        )
        try:
            sunflower = pvz.Sunflower(1, 2)
            sunflower.draw(screen, transparent_image)
            peashooter = pvz.Peashooter(2, 4)
            peashooter.draw(screen, transparent_image)
            zombie = pvz.Zombie(3, speed=0)
            zombie.x = 300
            zombie.draw(screen, transparent_image)
        finally:
            pvz.draw_ground_shadow = original_draw_ground_shadow

        self.assertEqual(
            calls,
            [
                (2 * pvz.CELL_SIZE + pvz.CELL_SIZE // 2, pvz.STATUS_H + 2 * pvz.CELL_SIZE - 4, (46, 10)),
                (4 * pvz.CELL_SIZE + pvz.CELL_SIZE // 2, pvz.STATUS_H + 3 * pvz.CELL_SIZE - 4, (58, 12)),
                (300 + pvz.ZOMBIE_WIDTH // 2, pvz.STATUS_H + 4 * pvz.CELL_SIZE - 4, (39, 8)),
            ],
        )

if __name__ == "__main__":
    unittest.main()
