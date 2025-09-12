import asyncio


async def pha_ca_phe():
    print("🧑‍🍳 Nhân viên bắt đầu pha cà phê (3s)...")
    await asyncio.sleep(3)
    print("✅ Nhân viên pha cà phê xong!")


async def lau_ban():
    print("🧹 Bạn bắt đầu lau bàn (2s)...")
    await asyncio.sleep(2)
    print("✅ Bạn lau bàn xong!")


async def main():
    print("📋 Bạn giao việc pha cà phê cho nhân viên.")
    task = asyncio.create_task(pha_ca_phe())  # Giao việc nhưng không chờ ngay

    print("👉 Bạn tranh thủ đi lau bàn.")
    await lau_ban()  # Làm việc khác trong khi cà phê đang pha

    print("⌛ Bạn quay lại và đợi cà phê nếu chưa xong.")
    await task  # Giờ mới đợi cà phê nếu cần

    print("🎉 Xong việc cả hai!")


asyncio.run(main())

# 🌀 event loop xử lý thế nào?
# ⏱ 0.00s
# create_task(pha_ca_phe()): task A được lên lịch

# await lau_ban(): chạy task B ngay

# ⏱ 0.00s → 2.00s
# Task B (lau_ban) đang await asyncio.sleep(2)

# Task A (pha_ca_phe) cũng bắt đầu và await asyncio.sleep(3)

# event loop đang chờ cả 2 sleep()

# ⏱ 2.00s
# lau_ban xong → tiếp tục dòng tiếp theo

# await task: chờ task A (pha cà phê)

# ⏱ 3.00s
# pha_ca_phe xong → event loop resume lại main() → in ra “🎉 Xong việc”
