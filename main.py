import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main():
    print("Hello from introduction!")
    print(device)


if __name__ == "__main__":
    main()
