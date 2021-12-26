class FuzzyLogicController:

    def __init__(self):
        # X axis
        self.x_in_max_val = 240 # frame width = 480 px
        self.x_out_max_val = 41 # camera view = 82.6 deg
        self.x_num_of_ranges = 5 # both for in and out values

    def calculate_x(self, x_in):
        in_range, out_range = self.find_ranges(x_in, self.x_in_max_val, self.x_out_max_val, self.x_num_of_ranges)

        in_a = (x_in - in_range[0]) / (in_range[0] - in_range[1]) + 1
        in_b = -(x_in - in_range[0]) / (in_range[0] - in_range[1])

        if in_a >= in_b:
            out_val = (in_a - 1) * (out_range[0] - out_range[1]) + out_range[0]
        else:
            out_val = out_range[0] - in_b * (out_range[0] - out_range[1])
        
        return int(out_val)

    def find_ranges(self, val, max_in_val, max_out_val, num_of_ranges):
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

if __name__ == "__main__":
    flc = FuzzyLogicController()
    print(flc.calculate_x(130))