import numpy as np
import matplotlib.pyplot as plt


def classical_random_walk(steps=50, trials=1000):
    final_positions = []

    for _ in range(trials):
        position = 0

        for _ in range(steps):
            step = np.random.choice([-1, 1])  # left or right
            position += step

        final_positions.append(position)

    return final_positions



def plot_classical(results, steps):
    plt.hist(results, bins=range(-steps, steps + 2), density=True)
    plt.title("Classical Random Walk Distribution")
    plt.xlabel("Position")
    plt.ylabel("Probability")
    plt.show()

# if __name__ == "__main__":
#     steps = 50
#     results = classical_random_walk(steps=steps)
    
#     print(results[:10])
#     plot_classical(results, steps)