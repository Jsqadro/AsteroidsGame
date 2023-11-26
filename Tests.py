import unittest
import pygame
from unittest.mock import Mock, patch
from main import Asteroid, Bullet, UFO, EnemyBullet, LifeBonus, GunUpgradeBonus, Player

class TestPlayerMovement(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.player = Player()

class TestAsteroid(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.asteroid = Asteroid(30, "asteroid_level1.png")

    def test_asteroid_creation(self):
        self.assertEqual(self.asteroid.speed, 2)
        self.assertGreaterEqual(self.asteroid.rect.width, 20)
        self.assertLessEqual(self.asteroid.rect.width, 50)

    def test_asteroid_movement(self):
        initial_rect_center = self.asteroid.rect.center
        score = 0
        self.asteroid.update(score)
        self.assertNotEqual(initial_rect_center, self.asteroid.rect.center)

class TestBullet(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.bullet = Bullet(100, 200, 45)

    def test_bullet_creation(self):
        self.assertEqual(self.bullet.speed, 15)

    def test_bullet_movement(self):
        initial_rect_center = self.bullet.rect.center
        self.bullet.update()
        self.assertNotEqual(initial_rect_center, self.bullet.rect.center)

class TestUFO(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.ufo = UFO()

    def test_ufo_creation(self):
        self.assertEqual(self.ufo.speed, 2)

    def test_ufo_movement(self):
        initial_rect_center = self.ufo.rect.center
        self.ufo.update()
        self.assertNotEqual(initial_rect_center, self.ufo.rect.center)

    def test_ufo_attack_player(self):
        player = Player()
        self.ufo.attack_player(player)
        self.assertTrue(player.rect.centerx > 0 and player.rect.centery > 0)

class TestEnemyBullet(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.enemy_bullet = EnemyBullet(100, 200, 45)

    def test_enemy_bullet_creation(self):
        self.assertEqual(self.enemy_bullet.speed, 10)

    def test_enemy_bullet_movement(self):
        initial_rect_center = self.enemy_bullet.rect.center
        self.enemy_bullet.update()
        self.assertNotEqual(initial_rect_center, self.enemy_bullet.rect.center)

class TestLifeBonus(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.life_bonus = LifeBonus()

    def test_life_bonus_respawn(self):
        initial_rect_center = self.life_bonus.rect.center
        self.life_bonus.respawn_bonus()
        self.assertNotEqual(initial_rect_center, self.life_bonus.rect.center)

class TestGunUpgradeBonus(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.gun_upgrade_bonus = GunUpgradeBonus()

    def test_gun_upgrade_bonus_respawn(self):
        initial_rect_center = self.gun_upgrade_bonus.rect.center
        self.gun_upgrade_bonus.respawn_bonus()
        self.assertNotEqual(initial_rect_center, self.gun_upgrade_bonus.rect.center)

if __name__ == '__main__':
    unittest.main()
