import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from selenium.webdriver.common.action_chains import ActionChains
import random
import re
import psutil

# Danh sách các profile và biến quản lý
PROFILES = ['10', '11', '18', '19', '23']
current_profile_index = 0
jobs_done = 0
no_job_count = 0  # Biến đếm số lần gặp thông báo "chưa có jobs mới"

def get_next_profile():
    global current_profile_index
    current_profile_index = (current_profile_index + 1) % len(PROFILES)
    return PROFILES[current_profile_index]

def should_switch_profile(jobs_count):
    return jobs_count > 0 and jobs_count % 20 == 0

def get_profile_number():
    global current_profile_index
    return PROFILES[current_profile_index]

def restart_browser(driver):
    try:
        if driver:
            driver.quit()
            
        # Kill tất cả các tiến trình Chrome đang chạy
        try:
            # Tìm và kill tất cả các process chrome
            for proc in psutil.process_iter(['name']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            print("Đã đóng tất cả các tiến trình Chrome")
            time.sleep(2)  # Đợi các tiến trình được đóng hoàn toàn
        except Exception as e:
            print(f"Lỗi khi đóng các tiến trình Chrome: {str(e)}")
            
        # Khởi động lại browser với profile mới
        return setup_driver()
    except Exception as e:
        print(f"Lỗi khi khởi động lại trình duyệt: {str(e)}")
        return None

def setup_driver():
    # Đường dẫn đến thư mục User Data của Chrome
    user_data_dir = os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\User Data'
    
    # Lấy số profile từ người dùng
    profile_number = get_profile_number()
    
    # Cấu hình Chrome options
    options = uc.ChromeOptions()
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument(f'--profile-directory=Profile {profile_number}')
    
    # Stealth mode arguments
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-site-isolation-trials')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process,SitePerProcess')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--enable-javascript')
    
    # Thêm các arguments mới để tăng cường stealth
    options.add_argument('--disable-blink-features')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--window-size={1920 + random.randint(-100, 100)},{1080 + random.randint(-100, 100)}')
    options.add_argument(f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 108)}.0.0.0 Safari/537.36')
    
    # Khởi tạo driver với các tùy chọn đặc biệt
    driver = uc.Chrome(
        options=options,
        version_main=131,
        use_subprocess=True,
        headless=False
    )
    
    # Thêm JavaScript để vượt qua automation detection
    js_script = """
    // Override properties
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // Override permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
    
    // Override plugins
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            return [
                {
                    0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                },
                {
                    0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                    description: "Portable Document Format",
                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                    length: 1,
                    name: "Chrome PDF Viewer"
                }
            ];
        }
    });
    
    // Override languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['vi-VN', 'vi', 'en-US', 'en']
    });
    
    // Override platform
    Object.defineProperty(navigator, 'platform', {
        get: () => 'Win32'
    });
    
    // Override connection
    Object.defineProperty(navigator, 'connection', {
        get: () => {
            return {
                rtt: 100,
                downlink: 10,
                effectiveType: '4g',
                saveData: false
            };
        }
    });
    
    // Override hardware concurrency
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => 8
    });
    
    // Override device memory
    Object.defineProperty(navigator, 'deviceMemory', {
        get: () => 8
    });
    
    // Override Chrome
    window.chrome = {
        app: {
            InstallState: {
                DISABLED: 'disabled',
                INSTALLED: 'installed',
                NOT_INSTALLED: 'not_installed'
            },
            RunningState: {
                CANNOT_RUN: 'cannot_run',
                READY_TO_RUN: 'ready_to_run',
                RUNNING: 'running'
            },
            getDetails: function() {},
            getIsInstalled: function() {},
            installState: function() {},
            isInstalled: false,
            runningState: function() {}
        },
        runtime: {
            OnInstalledReason: {
                CHROME_UPDATE: 'chrome_update',
                INSTALL: 'install',
                SHARED_MODULE_UPDATE: 'shared_module_update',
                UPDATE: 'update'
            },
            OnRestartRequiredReason: {
                APP_UPDATE: 'app_update',
                OS_UPDATE: 'os_update',
                PERIODIC: 'periodic'
            },
            PlatformArch: {
                ARM: 'arm',
                ARM64: 'arm64',
                MIPS: 'mips',
                MIPS64: 'mips64',
                X86_32: 'x86-32',
                X86_64: 'x86-64'
            },
            PlatformNaclArch: {
                ARM: 'arm',
                MIPS: 'mips',
                MIPS64: 'mips64',
                X86_32: 'x86-32',
                X86_64: 'x86-64'
            },
            PlatformOs: {
                ANDROID: 'android',
                CROS: 'cros',
                LINUX: 'linux',
                MAC: 'mac',
                OPENBSD: 'openbsd',
                WIN: 'win'
            },
            RequestUpdateCheckStatus: {
                NO_UPDATE: 'no_update',
                THROTTLED: 'throttled',
                UPDATE_AVAILABLE: 'update_available'
            }
        }
    };
    """
    
    try:
        # Thực thi JavaScript trước khi load trang
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': js_script
        })
        
        # Thêm các CDP commands để tăng cường stealth
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        })
        
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": """
                Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 1});
                Object.defineProperty(navigator, 'msMaxTouchPoints', {get: () => 1});
                Object.defineProperty(navigator, 'webkitMaxTouchPoints', {get: () => 1});
            """
        })
        
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

def get_job_count_from_modal(driver):
    try:
        # Đợi modal xuất hiện và lấy nội dung
        modal_content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#swal2-content"))
        )
        
        # Tìm số job trong nội dung modal
        content_text = modal_content.text
        if "số jobs đã làm trong ngày" in content_text.lower():
            # Tìm số job bằng regex
            match = re.search(r'số jobs đã làm trong ngày\s*(\d+)', content_text.lower())
            if match:
                completed_jobs = int(match.group(1))
                print(f"Số job đã làm hôm nay: {completed_jobs}")
                
                # Kiểm tra xem có cần đổi profile không
                if should_switch_profile(completed_jobs):
                    next_profile = get_next_profile()
                    print(f"Đã đạt {completed_jobs} jobs. Chuyển sang profile {next_profile}")
                    return completed_jobs, True
                return completed_jobs, False
    except Exception as e:
        print(f"Không thể lấy số job từ modal: {str(e)}")
    return None, False

def switch_to_next_profile(driver):
    try:
        # Đóng driver hiện tại nếu có
        if driver:
            driver.quit()
            
        # Kill tất cả các tiến trình Chrome đang chạy
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            print("Đã đóng tất cả các tiến trình Chrome")
            time.sleep(2)  # Đợi các tiến trình được đóng hoàn toàn
        except Exception as e:
            print(f"Lỗi khi đóng các tiến trình Chrome: {str(e)}")
        
        # Lấy profile tiếp theo
        next_profile = get_next_profile()
        print(f"Chuyển sang profile {next_profile}")
        
        # Khởi động lại browser với profile mới
        new_driver = setup_driver()
        if new_driver:
            new_driver.get('https://app.golike.net/jobs/instagram')
            time.sleep(5)
            return new_driver
        return None
    except Exception as e:
        print(f"Lỗi khi chuyển profile: {str(e)}")
        return None

def check_reload_message(driver):
    try:
        global no_job_count
        # Kiểm tra thông báo trên modal
        modal_content = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "swal2-content"))
        )
        content_text = modal_content.text.lower()
        
        # Xử lý các loại thông báo
        if "vui lòng bấm lại load job" in content_text:
            print("Phát hiện thông báo:", modal_content.text)
            # Click nút OK trên modal
            ok_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.swal2-styled"))
            )
            ok_button.click()
            print("Đã click nút OK")
            time.sleep(2)  # Đợi modal đóng
            return True, driver
        elif "hiện tại chưa có jobs mới" in content_text:
            print("Phát hiện thông báo:", modal_content.text)
            no_job_count += 1
            print(f"Đã gặp thông báo không có job mới {no_job_count} lần")
            
            # Click nút OK trên modal
            ok_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.swal2-styled"))
            )
            ok_button.click()
            print("Đã click nút OK")
            time.sleep(2)  # Đợi modal đóng
            
            # Nếu gặp thông báo quá 5 lần, chuyển profile
            if no_job_count >= 5:
                print("Đã gặp thông báo không có job mới quá 5 lần, chuyển profile")
                no_job_count = 0  # Reset biến đếm
                new_driver = switch_to_next_profile(driver)
                if new_driver:
                    return True, new_driver
                else:
                    print("Không thể khởi tạo driver mới, tiếp tục với driver cũ")
                    return True, driver
            return True, driver
        return False, driver
    except:
        return False, driver

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
                    following_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Following') or contains(text(), 'Requested') or contains(text(), 'Đang theo dõi')]")
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
                # Đóng tab Instagram và quay lại tab Golike
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                # Chuyển sang profile tiếp theo do rate limit
                driver = switch_to_next_profile(driver)
                return False, True

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

                    time.sleep(1)
                    
                    # Đợi và click nút OK trên popup
                    ok_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm.swal2-styled"))
                    )
                    
                    # Lấy số job đã làm trước khi click OK
                    jobs_count, need_switch = get_job_count_from_modal(driver)
                    
                    ok_button.click()
                    print("Đã click nút OK")
                    time.sleep(2)  # Đợi popup đóng
                    
                    return True, need_switch
                else:
                    print("Không tìm thấy nút Hoàn thành")
                    return False, False
                
            except Exception as e:
                print(f"Không thể click nút Hoàn thành hoặc OK: {str(e)}")
                return False, False
                
            return True, False
        
        return False, False
        
    except Exception as e:
        print(f"Không thể thực hiện follow: {str(e)}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return False, False

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
                return False, False
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
            return False, False
        
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
                
                # Lấy số job đã làm trước khi click OK
                jobs_count, need_switch = get_job_count_from_modal(driver)
                
                ok_button.click()
                print("Đã click nút OK")
                time.sleep(2)  # Đợi popup đóng
                
                return True, need_switch
            else:
                print("Không tìm thấy nút Hoàn thành")
                return False, False
            
        except Exception as e:
            print(f"Không thể click nút Hoàn thành hoặc OK: {str(e)}")
            return False, False
            
        return True, False
        
    except Exception as e:
        print(f"Không thể thực hiện like: {str(e)}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return False, False

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
                reload_needed, driver = check_reload_message(driver)
                if reload_needed:
                    print("Đang chờ job mới...")
                    time.sleep(3)  # Đợi một chút trước khi tiếp tục
                    continue
                
                # Click nút Nhận Job ngay
                if click_nhan_job(driver):
                    time.sleep(2)
                    # Kiểm tra loại job
                    job_type = check_job_type(driver)
                    success, need_switch = False, False
                    
                    if job_type == "follow":
                        print("Đã tìm thấy job follow")
                        success, need_switch = perform_follow(driver)
                    elif job_type == "like":
                        print("Đã tìm thấy job like")
                        success, need_switch = perform_like(driver)
                    else:
                        print("Không phải job follow hoặc like, bỏ qua")
                        success, need_switch = False, False
                    
                    # Nếu job thành công và cần đổi profile hoặc bị rate limit
                    if need_switch:
                        driver = switch_to_next_profile(driver)
                        if not driver:
                            print("Không thể khởi tạo driver mới, thoát chương trình")
                            break
                
                time.sleep(3)  # Đợi một chút trước khi tìm job mới
                
            except Exception as e:
                print(f"Lỗi trong vòng lặp chính: {str(e)}")
                # Nếu có lỗi, thử refresh trang
                try:
                    driver.refresh()
                    time.sleep(5)
                except:
                    # Nếu không thể refresh, thử khởi động lại driver
                    print("Không thể refresh trang, thử khởi động lại driver")
                    driver = switch_to_next_profile(driver)
                    if not driver:
                        print("Không thể khởi tạo driver mới, thoát chương trình")
                        break
            
    except Exception as e:
        print(f"Có lỗi xảy ra: {str(e)}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()
