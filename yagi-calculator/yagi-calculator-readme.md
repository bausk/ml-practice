# Yagi Antenna Calculator

A Python application for designing and analyzing Yagi antennas. This tool helps radio enthusiasts, amateur radio operators, and RF engineers to calculate the central frequency, SWR bandwidth, and gain of Yagi antenna designs.

## Features

- Interactive GUI for designing Yagi antennas
- Add/remove/modify antenna elements (reflector, driven element, directors)
- Calculate central frequency based on driven element length
- Determine SWR < 1.5 and SWR < 2.0 bandwidth
- Estimate antenna gain
- Visualize SWR curve across frequency range
- Customize boom diameter and feed impedance

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/yagi-antenna-calculator.git
cd yagi-antenna-calculator
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Install Kivy Garden's matplotlib:
```
garden install matplotlib
```

## Usage

Run the application:
```
python yagi_antenna_calculator.py
```

### Designing an Antenna

1. Set the design frequency, boom diameter, and feed impedance in the top section
2. Add/remove elements using the buttons in the middle section
3. Adjust element parameters (type, length, diameter, position)
4. Click "Calculate" to see the results and SWR plot

### Understanding the Results

- **Central Frequency**: The resonant frequency of the antenna
- **SWR < 1.5 Bandwidth**: Frequency range where SWR is below 1.5:1
- **SWR < 2.0 Bandwidth**: Frequency range where SWR is below 2.0:1
- **Estimated Gain**: Approximate gain in dBi

## Technical Notes

- The application uses simplified models for SWR and gain calculations
- All dimensions are in metric units (meters, millimeters)
- Frequencies are in MHz
- The driven element is assumed to be a simple dipole with 50 Ohm impedance
- Element positions are measured from the reflector (position 0)

## Limitations

This tool provides approximations based on simplified models and is intended for educational and preliminary design purposes. For precise antenna design, consider using more advanced electromagnetic simulation software.

## License

MIT


# ar-practice-2025
AR Практика 2025 рік 3 курс