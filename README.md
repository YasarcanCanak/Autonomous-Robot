 Autonomous Target Tracking Robot

This project is an advanced robotic system design capable of autonomous target tracking through the integration of Computer Vision and Embedded Systems.

## 1. System Architecture
The system consists of two primary layers:
*   **Edge-AI Layer (PC):** An architecture utilizing YOLO11 for object detection and autonomous decision-making mechanisms.
*   **Control Layer (STM32):** A low-level reflex layer that translates directional commands into PWM signals for motor drivers.

## 2. Hardware Specifications
*   **Main Processor:** STM32F407 (ARM Cortex-M4)
*   **Imaging:** ESP32-CAM (Live stream via Wi-Fi)
*   **Motor Driver:** L298N H-Bridge
*   **Power:** 7.4V (2x18650 Li-ion batteries)

## 3. Software and Algorithms
*   **Object Detection:** `YOLO11` model architecture, trained on high-performance GPU clusters at **UHEM (National Center for High Performance Computing)**.
*   **Communication:** TCP/IP socket communication (PC - ESP32 - STM32 chain).
*   **Control:** Differential steering logic and error compensation for precise target tracking.
*   **Future Work:** Kalman Filter-based position estimation to minimize system latency.

## 4. Project Structure
- `/Firmware`: STM32 workspace and hardware firmware files.
- `/AI_Module`: Python-based autonomous tracking scripts and pre-trained model weights (.pt).

---
*This project is conducted by Yaşarcan within the scope of research and development for autonomous systems and defense industry applications.*
