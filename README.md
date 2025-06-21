# Adversarial Search: KTH Fishing Derby AI

## Project Overview
This project implements an **adversarial search algorithm** to optimize decision-making in the **KTH Fishing Derby Game**. The AI-controlled boat must **maximize its score** while strategically minimizing the opponent's advantage.

## Technologies & Tools Used
- **Programming Language**: Python
- **Algorithm**: Minimax with **Alpha-Beta Pruning**
- **Heuristics**: Score Differentials & Distance-Based Prioritization
- **Optimizations**: Move Ordering, Transposition Tables, Iterative Deepening

## Key Features
- **State Representation**: The game is modeled as a **turn-based grid search problem**.
- **Utility Function**: Computes **score differences** to evaluate advantage.
- **Alpha-Beta Pruning**: Optimizes Minimax by **eliminating unpromising branches**.
- **Move Ordering**: Prioritizes **high-impact actions first** to improve pruning efficiency.
- **Iterative Deepening**: Enables **deeper searches** while maintaining real-time constraints.

## Results
- The AI effectively **maximizes its score while blocking opponent actions**.  
- **Alpha-Beta Pruning significantly reduces search complexity**, improving performance.  
- **State caching** prevents redundant computations, enhancing efficiency.  
