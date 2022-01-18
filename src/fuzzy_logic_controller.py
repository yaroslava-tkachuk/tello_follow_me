"""Copyright 2022 Yaroslava Tkachuk. All rights reserved."""

class FuzzyLogicController:

    """Class for calculating command values using Fuzzy Logic algorithm.
    
    Membership function - triangular.
    Decision making method - max.
    In ranges are based on the maximum possible distance of the face bounding
    box from the frame center (in pixels).
    """

    #--------------------------------------------------------------------------
    # Init
    #--------------------------------------------------------------------------
    def __init__(self):
        # X axis
        # Frame width = 480 px.
        # Maximum value for 1 direction: 480 px // 2 = 240 px.
        self._x_in_max_val = 240 
        # Camera view = 82.6 deg.
        # Maximum value for 1 direction: 82.6 deg // 2 = 41 deg.
        self._x_out_max_val = 41
        self._x_num_of_ranges = 5 # Both for in and out values.

        # Z axis
        # Frame height = 360 px.
        # Maximum value for 1 direction: 360 px // 2 = 180 px.
        self._z_in_max_val = 180
        # Start altitude = approx. 150 cm, commands range = [-50 cm; +50 cm].
        self._z_out_max_val = 50
        self._z_num_of_ranges = 5 # Both for in and out values.

    #--------------------------------------------------------------------------
    # End Init
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Getters
    #--------------------------------------------------------------------------

    @property
    def x_in_max_val(self):
        return self._x_in_max_val

    @property
    def x_out_max_val(self):
        return self._x_out_max_val

    @property
    def x_num_of_ranges(self):
        return self._x_num_of_ranges

    @property
    def z_in_max_val(self):
        return self._z_in_max_val

    @property
    def z_out_max_val(self):
        return self._z_out_max_val

    @property
    def z_num_of_ranges(self):
        return self._z_num_of_ranges
    
    #--------------------------------------------------------------------------
    # End Getters
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Setters
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # End Setters
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Class Methods
    #--------------------------------------------------------------------------

    def calculate_x(self, x_in):
        return self.calculate_out_val(x_in, self.x_in_max_val,
            self.x_out_max_val, self.x_num_of_ranges)

    def calculate_z(self, z_in):
        return self.calculate_out_val(z_in, self.z_in_max_val,
            self.z_out_max_val, self.z_num_of_ranges)

    def calculate_out_val(self, val, max_in_val, max_out_val, num_of_ranges):

        """Calculates output value for the given input value.
        
        IN:
            val - int - input value.
            max_in_val - int - maximum possible input value.
            max_out_val - int - maximum possible output value.
            num_of_ranges - int - number of ranges, same for input and output.
        OUT:
            out_val - input - output value.
        """

        # Calculate input and output ranges.
        in_range, out_range = self.find_ranges(val, max_in_val, max_out_val,
            num_of_ranges)

        # Calculate 2 possible crisp values for the given range based on line
        # equation.
        in_a = (val - in_range[0]) / (in_range[0] - in_range[1]) + 1
        in_b = -(val - in_range[0]) / (in_range[0] - in_range[1])

        # Choose maximum crisp value and calculate output value based on line
        # equation.
        if in_a >= in_b:
            out_val = int((in_a - 1) * (out_range[0] - out_range[1]) + out_range[0])
        else:
            out_val = int(out_range[0] - in_b * (out_range[0] - out_range[1]))
        
        return out_val

    def find_ranges(self, val, max_in_val, max_out_val, num_of_ranges):

        """Calculates in and out ranges for the given input value.
        
        IN:
            val - int - input value.
            max_in_val - int - maximum possible input value.
            max_out_val - int - maximum possible output value.
            num_of_ranges - int - number of ranges, same for input and output.
        OUT:
            (in_range, out_range) - tuple - input and output ranges.
        """

        step_in = max_in_val // num_of_ranges
        step_out = max_out_val // num_of_ranges

        num_of_out_range = 0
        in_range = None

        for i in range(0, max_in_val+1, step_in):
            if val <= i:
                in_range = i-step_in, i
                break
            num_of_out_range += 1

        out_range = ((num_of_out_range-1)*step_out, num_of_out_range*step_out)

        return in_range, out_range

    #--------------------------------------------------------------------------
    # End Class Methods
    #--------------------------------------------------------------------------

if __name__ == "__main__":
    # For testing purposes.

    flc = FuzzyLogicController()

    print(flc.calculate_x(130))
    print(flc.calculate_z(100))
