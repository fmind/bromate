# %% EXECUTIONS

# with tempfile.NamedTemporaryFile(prefix="bromate-", suffix=".png") as screenshot_file:
#     state.web.save_screenshot(filename=screenshot_file.name)
#     screenshot = PIL.Image.open(fp=screenshot_file)
# history:
# - short: HTML + screenshot
# - long: action trace


# %% DRIVERS

# time.sleep(1)
# accept_button = driver.find_element(By.XPATH, "//button[contains(.,'Tout accepter')]")
# accept_button.click()
# elem = driver.find_element(By.NAME, "q")
# elem.send_keys("selenium")
# elem.submit()
# time.sleep(1)
# driver.save_screenshot("browser.png")
