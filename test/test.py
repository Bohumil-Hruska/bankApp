from app import sum

#python -m pytest name
def test_init():
    assert sum(1,2) == 3
    assert sum(4,4) == 8