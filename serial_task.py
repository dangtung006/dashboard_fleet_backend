import time
import random

# Giả lập các hàm nhiệm vụ
def A(): print("A done")
def B(): print("B doing..."); raise Exception("B failed")
def C(): print("C done")

# Callback sau mỗi hàm
def callback(success, error=None):
    print("success::: callback" , success)
    # if success:
    #     print(f"[✔️ Callback] {name} success.")
    # else:
    #     print(f"[❌ Callback] {name} failed after retry. Reason: {error}")

# Core logic
def run_with_retry(funcs, max_retries=3, callback=None):
    for f in funcs:
        retry_count = 0
        success = False
        while retry_count < max_retries:
            try:
                f()
                success = True
                print("aaaa")
                break
                print("bbbbbbb")
            except Exception as e:
                retry_count += 1
                print(f"[Retry] {f.__name__} failed: {e} ({retry_count}/{max_retries})")
                time.sleep(0.5)
                last_error = e
                
        if callback:
            # callback(f.__name__, success, error=last_error if not success else None)
            callback(success, error=last_error if not success else None)
        print("current func:  ", f.__name__)
        if not success:
            break  # stop entire pipeline if a function fails

run_with_retry([A, B, C], callback=callback)

