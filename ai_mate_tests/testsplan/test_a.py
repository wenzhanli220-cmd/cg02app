import time

import allure
import pytest

@allure.epic("加减乘除运算")
@allure.feature("二位运算")
@allure.story("加法")
@allure.title("加法")
@pytest.mark.ut
def test_case_01():
    time.sleep(1)  # 模拟用例执行耗时
    assert 1 + 1 == 2

@allure.epic("加减乘除运算")
@allure.feature("二位运算")
@allure.story("乘法")
@allure.title("乘法")
@pytest.mark.ut
def test_case_02():
    time.sleep(1)
    assert 2 * 3 == 6

@allure.epic("加减乘除运算")
@allure.feature("二位运算")
@allure.story("减法")
@allure.title("减法")
@pytest.mark.ut
def test_case_03():
    time.sleep(1)
    assert 5 - 2 == 3

@allure.epic("加减乘除运算")
@allure.feature("二位运算")
@allure.story("除法")
@allure.title("除法")
@pytest.mark.ut
def test_case_04():
    time.sleep(1)
    assert 4 / 2 == 3


@pytest.mark.web
def test_web(selenium):
    selenium.get("https://www.baidu.com")

    print(selenium.title)
    time.sleep(1)
    assert False