import math
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
try:
    from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
except ImportError:
    from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from kivy.core.window import Window
from kivy.metrics import dp

# Constants
SPEED_OF_LIGHT = 299792458  # m/s
IMPEDANCE_FREE_SPACE = 376.73  # ohms

class YagiElement:
    def __init__(self, element_type="Reflector", length=0.0, diameter=0.0, position=0.0):
        self.element_type = element_type  # Reflector, Driven, Director
        self.length = length  # in meters
        self.diameter = diameter  # in meters
        self.position = position  # distance from reflector in meters

class YagiAntennaCalculator:
    def __init__(self):
        self.elements = []
        self.boom_diameter = 0.0  # in meters
        self.frequency = 0.0  # in Hz
        self.impedance = 50.0  # in ohms
        
    def add_element(self, element):
        self.elements.append(element)
        
    def remove_element(self, index):
        if 0 <= index < len(self.elements):
            del self.elements[index]
            
    def calculate_central_frequency(self):
        """Calculate the central frequency based on the driven element length"""
        for element in self.elements:
            if element.element_type == "Driven":
                # Basic dipole formula: f = c / (2 * L)
                return SPEED_OF_LIGHT / (2 * element.length)
        return 0.0
    
    def calculate_swr(self, frequency):
        """
        Calculate SWR at a given frequency
        This is a simplified model based on approximations
        """
        if not self.elements:
            return float('inf')
            
        # Find driven element
        driven_element = None
        for element in self.elements:
            if element.element_type == "Driven":
                driven_element = element
                break
                
        if not driven_element:
            return float('inf')
            
        # Calculate wavelength
        wavelength = SPEED_OF_LIGHT / frequency
        
        # Calculate normalized length (length/wavelength)
        normalized_length = driven_element.length / wavelength
        
        # Simple approximation of impedance based on normalized length
        # This is a very simplified model
        if 0.45 <= normalized_length <= 0.55:
            # Near resonance
            deviation = abs(0.5 - normalized_length)
            # Approximate impedance change
            z_antenna = complex(50 + 300 * deviation, 100 * deviation)
        else:
            # Far from resonance
            z_antenna = complex(50 + 500 * abs(0.5 - normalized_length), 
                               200 * (normalized_length - 0.5))
        
        # Calculate reflection coefficient
        z0 = self.impedance  # characteristic impedance
        gamma = abs((z_antenna - z0) / (z_antenna + z0))
        
        # Calculate SWR
        if gamma < 1:
            return (1 + gamma) / (1 - gamma)
        else:
            return float('inf')
    
    def find_swr_bandwidth(self, swr_threshold):
        """Find the bandwidth where SWR is below the threshold"""
        central_freq = self.calculate_central_frequency()
        if central_freq == 0:
            return (0, 0)
            
        # Search for lower frequency bound
        f_lower = central_freq
        step = central_freq / 100
        while self.calculate_swr(f_lower) < swr_threshold and f_lower > central_freq / 2:
            f_lower -= step
            
        # Search for upper frequency bound
        f_upper = central_freq
        while self.calculate_swr(f_upper) < swr_threshold and f_upper < central_freq * 2:
            f_upper += step
            
        return (f_lower, f_upper)
        
    def calculate_gain(self):
        """
        Calculate approximate gain of the Yagi antenna
        This is a very simplified model
        """
        if len(self.elements) < 2:
            return 0.0
            
        # Count directors
        num_directors = sum(1 for e in self.elements if e.element_type == "Director")
        
        # Basic approximation: gain increases with number of directors
        # Starting with ~7 dBi for a 3-element Yagi (1 reflector, 1 driven, 1 director)
        # Each additional director adds ~1 dBi up to a point
        if num_directors == 0:
            return 5.0  # Simple dipole with reflector
        else:
            return 7.0 + min(num_directors - 1, 8) * 1.0  # Capped at ~15 dBi
            
    def plot_swr_curve(self):
        """Generate SWR vs Frequency plot"""
        central_freq = self.calculate_central_frequency()
        if central_freq == 0:
            return None
            
        # Create frequency range around central frequency
        freq_range = np.linspace(central_freq * 0.8, central_freq * 1.2, 100)
        swr_values = [self.calculate_swr(f) for f in freq_range]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(freq_range / 1e6, swr_values)  # Convert to MHz for display
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('SWR')
        ax.set_title('SWR vs Frequency')
        ax.grid(True)
        
        # Add horizontal lines for SWR thresholds
        ax.axhline(y=1.5, color='g', linestyle='--', alpha=0.7)
        ax.axhline(y=2.0, color='r', linestyle='--', alpha=0.7)
        
        # Set y-axis limits
        ax.set_ylim(1, 5)
        
        return fig

class ElementWidget(BoxLayout):
    def __init__(self, index, element, remove_callback, **kwargs):
        super(ElementWidget, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(40)  # Fixed height for each element row
        self.index = index
        self.element = element
        self.remove_callback = remove_callback
        
        # Element type spinner
        self.type_spinner = Spinner(
            text=element.element_type,
            values=('Reflector', 'Driven', 'Director'),
            size_hint=(0.2, 1)
        )
        self.type_spinner.bind(text=self.on_type_change)
        
        # Length input
        length_layout = BoxLayout(orientation='horizontal', size_hint=(0.25, 1))
        length_layout.add_widget(Label(text='Length (m):', size_hint=(0.5, 1)))
        self.length_input = TextInput(
            text=str(element.length),
            multiline=False,
            size_hint=(0.5, 1),
            input_filter='float'
        )
        self.length_input.bind(text=self.on_length_change)
        length_layout.add_widget(self.length_input)
        
        # Diameter input
        diameter_layout = BoxLayout(orientation='horizontal', size_hint=(0.25, 1))
        diameter_layout.add_widget(Label(text='Diameter (mm):', size_hint=(0.5, 1)))
        self.diameter_input = TextInput(
            text=str(element.diameter * 1000),  # Convert to mm for display
            multiline=False,
            size_hint=(0.5, 1),
            input_filter='float'
        )
        self.diameter_input.bind(text=self.on_diameter_change)
        diameter_layout.add_widget(self.diameter_input)
        
        # Position input
        position_layout = BoxLayout(orientation='horizontal', size_hint=(0.25, 1))
        position_layout.add_widget(Label(text='Position (m):', size_hint=(0.5, 1)))
        self.position_input = TextInput(
            text=str(element.position),
            multiline=False,
            size_hint=(0.5, 1),
            input_filter='float'
        )
        self.position_input.bind(text=self.on_position_change)
        position_layout.add_widget(self.position_input)
        
        # Remove button
        self.remove_button = Button(
            text='Remove',
            size_hint=(0.1, 1)
        )
        self.remove_button.bind(on_press=self.on_remove)
        
        # Add widgets to layout
        self.add_widget(self.type_spinner)
        self.add_widget(length_layout)
        self.add_widget(diameter_layout)
        self.add_widget(position_layout)
        self.add_widget(self.remove_button)
        
    def on_type_change(self, spinner, text):
        self.element.element_type = text
        
    def on_length_change(self, instance, value):
        try:
            self.element.length = float(value)
        except ValueError:
            pass
            
    def on_diameter_change(self, instance, value):
        try:
            # Convert from mm to m
            self.element.diameter = float(value) / 1000
        except ValueError:
            pass
            
    def on_position_change(self, instance, value):
        try:
            self.element.position = float(value)
        except ValueError:
            pass
            
    def on_remove(self, instance):
        self.remove_callback(self.index)

class YagiAntennaApp(App):
    def build(self):
        self.title = 'Yagi Antenna Calculator'
        Window.size = (1000, 700)
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Top section - Antenna parameters
        top_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=dp(10))
        
        # Boom diameter input
        boom_layout = BoxLayout(orientation='vertical', size_hint=(0.2, 1))
        boom_layout.add_widget(Label(text='Boom Diameter (mm)'))
        self.boom_input = TextInput(
            text='25.0',
            multiline=False,
            input_filter='float'
        )
        boom_layout.add_widget(self.boom_input)
        
        # Frequency input
        freq_layout = BoxLayout(orientation='vertical', size_hint=(0.2, 1))
        freq_layout.add_widget(Label(text='Design Frequency (MHz)'))
        self.freq_input = TextInput(
            text='144.0',
            multiline=False,
            input_filter='float'
        )
        freq_layout.add_widget(self.freq_input)
        
        # Impedance input
        imp_layout = BoxLayout(orientation='vertical', size_hint=(0.2, 1))
        imp_layout.add_widget(Label(text='Feed Impedance (Ω)'))
        self.imp_input = TextInput(
            text='50.0',
            multiline=False,
            input_filter='float'
        )
        imp_layout.add_widget(self.imp_input)
        
        # Calculate button
        button_layout = BoxLayout(orientation='vertical', size_hint=(0.2, 1))
        self.calculate_button = Button(text='Calculate')
        self.calculate_button.bind(on_press=self.on_calculate)
        button_layout.add_widget(self.calculate_button)
        
        # Adjust Frequency button
        adjust_button_layout = BoxLayout(orientation='vertical', size_hint=(0.2, 1))
        self.adjust_freq_button = Button(text='Adjust Freq')
        self.adjust_freq_button.bind(on_press=self.on_adjust_frequency)
        adjust_button_layout.add_widget(self.adjust_freq_button)
        
        # Add to top layout
        top_layout.add_widget(boom_layout)
        top_layout.add_widget(freq_layout)
        top_layout.add_widget(imp_layout)
        top_layout.add_widget(button_layout)
        top_layout.add_widget(adjust_button_layout)
        
        # Middle section - Elements list
        middle_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.35), spacing=dp(5))
        
        # Header for elements
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=dp(5))
        header_layout.add_widget(Label(text='Element Type', size_hint=(0.2, 1)))
        header_layout.add_widget(Label(text='Length (m)', size_hint=(0.25, 1)))
        header_layout.add_widget(Label(text='Diameter (mm)', size_hint=(0.25, 1)))
        header_layout.add_widget(Label(text='Position (m)', size_hint=(0.25, 1)))
        header_layout.add_widget(Label(text='', size_hint=(0.1, 1)))  # Placeholder for remove button
        
        # Scrollable elements list
        self.elements_scroll = ScrollView(size_hint=(1, 0.7))
        self.elements_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.elements_layout.bind(minimum_height=self.elements_layout.setter('height'))
        self.elements_scroll.add_widget(self.elements_layout)
        
        # Add element button
        self.add_element_button = Button(
            text='Add Element',
            size_hint=(1, 0.15)
        )
        self.add_element_button.bind(on_press=self.on_add_element)
        
        # Add to middle layout
        middle_layout.add_widget(header_layout)
        middle_layout.add_widget(self.elements_scroll)
        middle_layout.add_widget(self.add_element_button)
        
        # Bottom section - Results and plot
        bottom_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.5))
        
        # Results section
        results_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        
        # Central frequency
        cf_layout = BoxLayout(orientation='vertical', size_hint=(0.25, 1))
        cf_layout.add_widget(Label(text='Central Frequency (MHz)'))
        self.cf_result = Label(text='0.0')
        cf_layout.add_widget(self.cf_result)
        
        # SWR < 1.5 bandwidth
        swr15_layout = BoxLayout(orientation='vertical', size_hint=(0.25, 1))
        swr15_layout.add_widget(Label(text='SWR < 1.5 Bandwidth (MHz)'))
        self.swr15_result = Label(text='0.0 - 0.0')
        swr15_layout.add_widget(self.swr15_result)
        
        # SWR < 2.0 bandwidth
        swr20_layout = BoxLayout(orientation='vertical', size_hint=(0.25, 1))
        swr20_layout.add_widget(Label(text='SWR < 2.0 Bandwidth (MHz)'))
        self.swr20_result = Label(text='0.0 - 0.0')
        swr20_layout.add_widget(self.swr20_result)
        
        # Gain
        gain_layout = BoxLayout(orientation='vertical', size_hint=(0.25, 1))
        gain_layout.add_widget(Label(text='Estimated Gain (dBi)'))
        self.gain_result = Label(text='0.0')
        gain_layout.add_widget(self.gain_result)
        
        # Add to results layout
        results_layout.add_widget(cf_layout)
        results_layout.add_widget(swr15_layout)
        results_layout.add_widget(swr20_layout)
        results_layout.add_widget(gain_layout)
        
        # Plot area
        self.plot_layout = BoxLayout(size_hint=(1, 0.8))
        
        # Add to bottom layout
        bottom_layout.add_widget(results_layout)
        bottom_layout.add_widget(self.plot_layout)
        
        # Add all sections to main layout
        main_layout.add_widget(top_layout)
        main_layout.add_widget(middle_layout)
        main_layout.add_widget(bottom_layout)
        
        # Initialize calculator
        self.calculator = YagiAntennaCalculator()
        
        # Add default elements
        self.add_default_elements()
        
        return main_layout
        
    def add_default_elements(self):
        # Add default 3-element Yagi for 144 MHz
        reflector = YagiElement("Reflector", 1.03, 0.008, 0.0)
        driven = YagiElement("Driven", 0.98, 0.008, 0.25)
        director = YagiElement("Director", 0.93, 0.008, 0.5)
        
        self.calculator.add_element(reflector)
        self.calculator.add_element(driven)
        self.calculator.add_element(director)
        
        self.update_elements_display()
        
    def update_elements_display(self):
        self.elements_layout.clear_widgets()
        self.elements_layout.height = 0  # Reset height
        
        for i, element in enumerate(self.calculator.elements):
            element_widget = ElementWidget(i, element, self.remove_element)
            self.elements_layout.add_widget(element_widget)
            self.elements_layout.height += element_widget.height + dp(5)  # Add widget height plus spacing
            
    def on_add_element(self, instance):
        # Default to director if we already have reflector and driven
        element_type = "Director"
        if not any(e.element_type == "Reflector" for e in self.calculator.elements):
            element_type = "Reflector"
        elif not any(e.element_type == "Driven" for e in self.calculator.elements):
            element_type = "Driven"
            
        # Default position is after the last element
        position = 0.0
        if self.calculator.elements:
            position = max(e.position for e in self.calculator.elements) + 0.25
            
        # Default length based on element type (for 144 MHz)
        length = 0.93  # Director
        if element_type == "Reflector":
            length = 1.03
        elif element_type == "Driven":
            length = 0.98
            
        new_element = YagiElement(element_type, length, 0.008, position)
        self.calculator.add_element(new_element)
        self.update_elements_display()
        
    def remove_element(self, index):
        self.calculator.remove_element(index)
        self.update_elements_display()
        
    def on_calculate(self, instance):
        # Update calculator parameters
        try:
            self.calculator.boom_diameter = float(self.boom_input.text) / 1000  # Convert mm to m
            self.calculator.frequency = float(self.freq_input.text) * 1e6  # Convert MHz to Hz
            self.calculator.impedance = float(self.imp_input.text)
        except ValueError:
            return
            
        # Calculate results
        central_freq = self.calculator.calculate_central_frequency()
        swr15_band = self.calculator.find_swr_bandwidth(1.5)
        swr20_band = self.calculator.find_swr_bandwidth(2.0)
        gain = self.calculator.calculate_gain()
        
        # Update result labels
        self.cf_result.text = f"{central_freq / 1e6:.2f}"
        self.swr15_result.text = f"{swr15_band[0] / 1e6:.2f} - {swr15_band[1] / 1e6:.2f}"
        self.swr20_result.text = f"{swr20_band[0] / 1e6:.2f} - {swr20_band[1] / 1e6:.2f}"
        self.gain_result.text = f"{gain:.1f}"
        
        # Update plot
        self.plot_layout.clear_widgets()
        fig = self.calculator.plot_swr_curve()
        if fig:
            self.plot_layout.add_widget(FigureCanvasKivyAgg(fig))
            
    def on_adjust_frequency(self, instance):
        """Scale all antenna elements to a new frequency"""
        try:
            # Get the current central frequency from the calculator
            current_central_freq = self.calculator.calculate_central_frequency()
            if current_central_freq == 0:
                return  # No driven element to calculate from
                
            # Get the target frequency from the input field
            target_freq = float(self.freq_input.text) * 1e6  # Convert MHz to Hz
            
            # Calculate scaling factor (inverse ratio of frequencies)
            scaling_factor = current_central_freq / target_freq
            
            # Scale all elements
            for element in self.calculator.elements:
                # Scale length and round to nearest millimeter (convert to mm, round, convert back to m)
                element.length = round(element.length * scaling_factor * 1000) / 1000
                
                # Scale diameter and round to nearest 0.1mm
                element.diameter = round(element.diameter * scaling_factor * 10000) / 10000
                
                # Scale position and round to nearest millimeter
                element.position = round(element.position * scaling_factor * 1000) / 1000
                
            # Scale boom diameter and round to nearest 0.1mm
            self.calculator.boom_diameter = round(self.calculator.boom_diameter * scaling_factor * 10) / 10
            self.boom_input.text = f"{self.calculator.boom_diameter * 1000:.1f}"  # Update display (mm)
            
            # Update the calculator's frequency
            self.calculator.frequency = target_freq
            
            # Update the display
            self.update_elements_display()
            
            # Calculate and update results
            self.on_calculate(None)
            
        except (ValueError, ZeroDivisionError):
            pass  # Handle invalid input gracefully

if __name__ == '__main__':
    YagiAntennaApp().run() 