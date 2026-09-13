print("""
GESTURE CONTROLLED GAME SUITE
----------------------------
1. Snake Game
2. Subway Runner
3. Car Racing
""")

choice = input("Enter your choice (1/2/3): ")

if choice == "1":
    import snake_game
elif choice == "2":
    import subway_runner
elif choice == "3":
    import car_racing
else:
    print("Invalid choice")