from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from selenium.webdriver.common.action_chains import ActionChains
import random

def get_profile_number():
    while True:
        try:
            profile_num = input("Nhập số profile Chrome bạn muốn sử dụng (ví dụ: 10, 11, 18, 19, 23...): ")
            if profile_num.isdigit() and int(profile_num) > 0:
                return profile_num
            else:
                print("Vui lòng nhập một số nguyên dương.")
        except ValueError:
            print("Vui lòng nhập một số hợp lệ.")

def setup_driver():
    # Đường dẫn đến thư mục profile Firefox
    profile_path = os.path.expanduser('~') + r'\AppData\Roaming\Mozilla\Firefox\Profiles\up0atl84.default-release'
    
    # Cấu hình Firefox options
    options = Options()
    options.set_preference('profile', profile_path)
    
    # Stealth mode arguments
    options.set_preference('dom.webdriver.enabled', False)
    options.set_preference('useAutomationExtension', False)
    options.set_preference('privacy.trackingprotection.enabled', False)
    options.set_preference('network.cookie.cookieBehavior', 0)
    options.set_preference('general.useragent.override', f'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{random.randint(90, 108)}.0) Gecko/20100101 Firefox/{random.randint(90, 108)}.0')
    
    # Khởi tạo driver với các tùy chọn đặc biệt
    driver = webdriver.Firefox(options=options)
    
    # Thêm JavaScript để vượt qua automation detection
    js_script = """
    // Override properties
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // Override languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['vi-VN', 'vi', 'en-US', 'en']
    });
    
    // Override platform
    Object.defineProperty(navigator, 'platform', {
        get: () => 'Win32'
    });
    """
    
    try:
        # Thực thi JavaScript
        driver.execute_script(js_script)
        
    except Exception as e:
        print(f"Lỗi khi thực thi JavaScript: {str(e)}")
    
    return driver

def click_nhan_job(driver):
    try:
        # Đợi cho nút "Nhận Job ngay" xuất hiện và có thể click được
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.btn.btn-outline-light"))
        )
        # Click vào nút
        button.click()
        print("Đã click nút Nhận Job ngay")
        return True
    except Exception as e:
        print(f"Không thể click nút Nhận Job ngay: {str(e)}")
        return False

def check_job_type(driver):
    try:
        # Đợi và kiểm tra loại job
        job_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "d400"))
        ).text
        if "TĂNG LƯỢT THEO DÕI" in job_text:
            return "follow"
        elif "TĂNG LIKE CHO BÀI VIẾT" in job_text:
            return "like"
        return None
    except Exception as e:
        print(f"Không thể kiểm tra loại job: {str(e)}")
        return None

def handle_instagram_error(driver):
    try:
        # Đóng tab Instagram
        driver.close()
        # Chuyển về tab Golike
        driver.switch_to.window(driver.window_handles[0])
        
        # Tìm và click nút Báo lỗi
        error_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Báo lỗi')]"))
        )
        error_button.click()
        print("Đã click nút Báo lỗi")
        
        # Đợi và thử nhiều cách để click nút Gửi báo cáo
        report_button_selectors = [
            (By.CSS_SELECTOR, "button.btn.btn-primary.btn-sm.form-control.mt-3"),
            (By.XPATH, "//button[contains(text(), 'Gửi báo cáo')]"),
            (By.CSS_SELECTOR, "[type='submit'].btn.btn-primary")
        ]
        
        report_clicked = False
        for by, selector in report_button_selectors:
            try:
                report_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, selector))
                )
                
                # Thử click bằng selenium click thông thường
                try:
                    report_button.click()
                    report_clicked = True
                    print("Đã click Gửi báo cáo bằng click thông thường")
                    break
                except:
                    # Thử click bằng JavaScript
                    try:
                        driver.execute_script("arguments[0].click();", report_button)
                        report_clicked = True
                        print("Đã click Gửi báo cáo bằng JavaScript")
                        break
                    except:
                        # Thử click bằng ActionChains
                        try:
                            ActionChains(driver).move_to_element(report_button).click().perform()
                            report_clicked = True
                            print("Đã click Gửi báo cáo bằng ActionChains")
                            break
                        except:
                            continue
            except:
                continue
                
        if not report_clicked:
            print("Không thể click nút Gửi báo cáo")
            return False
        
        # Đợi và click nút OK trên modal
        ok_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.swal2-styled"))
        )
        ok_button.click()
        print("Đã click nút OK trên modal")
        time.sleep(2)  # Đợi modal đóng
        
        return True
    except Exception as e:
        print(f"Lỗi khi xử lý báo lỗi: {str(e)}")
        return False

def perform_follow(driver):
    try:
        # Click vào link Instagram
        instagram_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.bg-button-1"))
        )
        instagram_link.click()
        
        # Chuyển sang tab mới
        time.sleep(5)  # Đợi tab mới mở
        driver.switch_to.window(driver.window_handles[-1])
        
        # Đợi trang Instagram load hoàn tất
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        
        # Kiểm tra trang không khả dụng hoặc private
        try:
            error_text = driver.find_element(By.XPATH, "//span[contains(text(), 'Sorry, this page isn')]")
            if error_text:
                print("Phát hiện trang Instagram không khả dụng")
                return handle_instagram_error(driver)
        except:
            pass

        # Kiểm tra tài khoản private
        try:
            private_text = driver.find_element(By.XPATH, "//span[contains(text(), 'This account is private')]")
            if private_text:
                print("Phát hiện tài khoản Instagram private")
                return handle_instagram_error(driver)
        except:
            pass
        
        # Thử click Follow với nhiều cách khác nhau
        follow_clicked = False
        max_retries = 3  # Số lần thử tối đa
        current_retry = 0
        
        while current_retry < max_retries:
            try:
                # Kiểm tra xem đã follow chưa
                try:
                    following_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Following') or contains(text(), 'Requested')]")
                    print("Đã follow tài khoản này trước đó")
                    follow_clicked = True
                    break
                except:
                    # Thử nhiều cách để tìm và click nút Follow
                    follow_selectors = [
                        (By.CSS_SELECTOR, "._acan._acap._acas"),
                        (By.XPATH, "//button[text()='Follow']"),
                        (By.XPATH, "//button[contains(@class, '_acan') and contains(@class, '_acap')]"),
                        (By.CSS_SELECTOR, "[role='button']._acan._acap._acas")
                    ]
                    
                    for by, selector in follow_selectors:
                        try:
                            follow_button = WebDriverWait(driver, 3).until(
                                EC.element_to_be_clickable((by, selector))
                            )
                            # Thử các cách click khác nhau
                            try:
                                follow_button.click()
                            except:
                                try:
                                    driver.execute_script("arguments[0].click();", follow_button)
                                except:
                                    try:
                                        ActionChains(driver).move_to_element(follow_button).click().perform()
                                    except:
                                        continue
                            
                            # Đợi và kiểm tra nút Following
                            time.sleep(3)
                            try:
                                following_check = driver.find_element(By.CSS_SELECTOR, "button._acan._acap._acat._aj1-._ap30")
                                following_text = following_check.find_element(By.CSS_SELECTOR, "div._ap3a._aaco._aacw._aad6._aade").text
                                if following_text == "Following":
                                    print(f"Đã click Follow thành công sau {current_retry + 1} lần thử")
                                    follow_clicked = True
                                    break
                            except:
                                print(f"Chưa thấy nút Following sau lần thử thứ {current_retry + 1}")
                                if current_retry < max_retries - 1:
                                    print("Đang refresh trang và thử lại...")
                                    driver.refresh()
                                    time.sleep(5)
                            
                        except:
                            continue
                    
                    if follow_clicked:
                        break
                    
            except Exception as e:
                print(f"Lỗi khi thử follow lần {current_retry + 1}: {str(e)}")
            
            current_retry += 1
            if current_retry == max_retries:
                print("Tài khoản Instagram đã bị rate limited")
                driver.quit()
                exit()

        time.sleep(3)

        # Đóng tab Instagram và quay lại tab Golike
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
        if follow_clicked:
            # Click nút Hoàn thành
            try:
                # Tìm tất cả các button
                buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
                )
                
                # Tìm nút có chữ "Hoàn thành"
                complete_button = None
                for button in buttons:
                    try:
                        if "Hoàn thành" in button.text.strip():
                            complete_button = button
                            break
                    except:
                        continue
                
                if complete_button:
                    # Scroll đến nút nếu cần
                    driver.execute_script("arguments[0].scrollIntoView(true);", complete_button)
                    time.sleep(1)
                    
                    # Click nút Hoàn thành
                    complete_button.click()
                    print("Đã click nút Hoàn thành")
                    
                    # Đợi và click nút OK trên popup
                    ok_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.swal2-styled"))
                    )
                    ok_button.click()
                    print("Đã click nút OK")
                    time.sleep(2)  # Đợi popup đóng
                else:
                    print("Không tìm thấy nút Hoàn thành")
                    return False
                
            except Exception as e:
                print(f"Không thể click nút Hoàn thành hoặc OK: {str(e)}")
                return False
                
            return True
        
        return False
        
    except Exception as e:
        print(f"Không thể thực hiện follow: {str(e)}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return False

def perform_like(driver):
    try:
        # Click vào link Instagram
        instagram_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.bg-button-1"))
        )
        instagram_link.click()
        
        # Chuyển sang tab mới
        time.sleep(5)  # Đợi tab mới mở
        driver.switch_to.window(driver.window_handles[-1])
        
        # Đợi trang Instagram load hoàn tất
        WebDriverWait(driver, 10).until(
            lambda x: "instagram.com" in x.current_url
        )
        time.sleep(2)
        
        # Kiểm tra trang không khả dụng hoặc private
        try:
            error_text = driver.find_element(By.XPATH, "//span[contains(text(), 'Sorry, this page isn')]")
            if error_text:
                print("Phát hiện trang Instagram không khả dụng")
                return handle_instagram_error(driver)
        except:
            pass

        # Kiểm tra tài khoản private
        try:
            private_text = driver.find_element(By.XPATH, "//span[contains(text(), 'This account is private')]")
            if private_text:
                print("Phát hiện tài khoản Instagram private")
                return handle_instagram_error(driver)
        except:
            pass
        
        try:
            # Kiểm tra xem đã like chưa
            try:
                unlike_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="button"] svg[aria-label="Unlike"]'))
                )
                print("Bài viết này đã được like trước đó")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                return False
            except:
                pass

            # Tìm và click nút Like
            like_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.x1i10hfl.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x6s0dn4.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x1ypdohk.x78zum5.xl56j7k.x1y1aw1k.x1sxyh0.xwib8y2.xurb0ha.xcdnw81'))
            )
            driver.execute_script("arguments[0].click();", like_button)
            print("Đã click nút Like trên Instagram")
            time.sleep(1)
            
        except Exception as e:
            print(f"Lỗi khi click nút Like: {str(e)}")
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            return False
        
        time.sleep(3)
        
        # Đóng tab Instagram và quay lại tab Golike
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
        # Click nút Hoàn thành
        try:
            # Tìm tất cả các button
            buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
            )
            
            # Tìm nút có chữ "Hoàn thành"
            complete_button = None
            for button in buttons:
                try:
                    if "Hoàn thành" in button.text.strip():
                        complete_button = button
                        break
                except:
                    continue
            
            if complete_button:
                # Scroll đến nút nếu cần
                driver.execute_script("arguments[0].scrollIntoView(true);", complete_button)
                time.sleep(1)
                
                # Click nút Hoàn thành
                complete_button.click()
                print("Đã click nút Hoàn thành")
                
                # Đợi và click nút OK trên popup
                ok_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.swal2-styled"))
                )
                ok_button.click()
                print("Đã click nút OK")
                time.sleep(2)  # Đợi popup đóng
            else:
                print("Không tìm thấy nút Hoàn thành")
                return False
            
        except Exception as e:
            print(f"Không thể click nút Hoàn thành hoặc OK: {str(e)}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Không thể thực hiện like: {str(e)}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return False

def check_reload_message(driver):
    try:
        # Kiểm tra thông báo "Vui lòng bấm lại load job"
        reload_message = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "swal2-content"))
        )
        if "Vui lòng bấm lại load job" in reload_message.text:
            print("Phát hiện thông báo yêu cầu load lại job")
            # Click nút OK trên modal
            ok_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.swal2-styled"))
            )
            ok_button.click()
            print("Đã click nút OK")
            time.sleep(2)  # Đợi modal đóng
            return True
        return False
    except:
        return False

def main():
    try:
        # Khởi tạo driver
        driver = setup_driver()
        
        # Truy cập trang Golike
        driver.get('https://app.golike.net/jobs/instagram')
        
        # Đợi để trang load hoàn toàn
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        while True:
            try:
                # Kiểm tra thông báo reload
                if check_reload_message(driver):
                    print("Đang chờ job mới...")
                    time.sleep(3)  # Đợi một chút trước khi tiếp tục
                    continue
                
                # Click nút Nhận Job ngay
                if click_nhan_job(driver):
                    time.sleep(2)
                    # Kiểm tra loại job
                    job_type = check_job_type(driver)
                    if job_type == "follow":
                        print("Đã tìm thấy job follow")
                        perform_follow(driver)
                    elif job_type == "like":
                        print("Đã tìm thấy job like")
                        perform_like(driver)
                    else:
                        print("Không phải job follow hoặc like, bỏ qua")
                
                time.sleep(3)  # Đợi một chút trước khi tìm job mới
                
            except Exception as e:
                print(f"Lỗi trong vòng lặp chính: {str(e)}")
                # Nếu có lỗi, thử refresh trang
                try:
                    driver.refresh()
                    time.sleep(5)
                except:
                    pass
            
    except Exception as e:
        print(f"Có lỗi xảy ra: {str(e)}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()
