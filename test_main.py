import pytest
from main import move_player, move_bullet, is_collision

def test_is_collision():
    assert is_collision(100, 100, 100, 100) is True
    assert is_collision(100, 100, 150, 150) is False
    
def test_move_bullet():
    bullet_y, bullet_state = move_bullet(0, "fire")
    assert bullet_state == "ready"
    bullet_y, bullet_state = move_bullet(100, "fire")
    assert bullet_state == "fire"
    
def test_move_player():
    player_x, player_y = move_player(0, 736, -0.5, 0.5)
    assert player_x == 0
    assert player_y == 736
    
    player_x, player_y = move_player(736, 736, 1, 1)
    assert player_x == 736
    assert player_y == 736
    
