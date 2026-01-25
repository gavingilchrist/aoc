class Program(object):
    def __init__(self, instr, input_val, verbose=False):
        self.ops = {
            1: self.do_add,
            2: self.do_mult,
            3: self.do_input,
            4: self.do_output,
            5: self.do_jump_if_true,
            6: self.do_jump_if_false,
            7: self.do_less_than,
            8: self.do_equals,
            9: self.do_adjust_relbase,
            }
        self.instr_orig = instr
        self.input_val_orig = input_val
        self.instr = []
        self.input_val = []
        self.output = []
        self.reset()
        self.verbose = verbose
        
    def reset(self):
        self.instr.clear()
        self.instr.extend(self.instr_orig)
        self.input_val.clear()
        self.input_val.extend(self.input_val_orig)
        self.output.clear()
        self.ptr = 0
        self.relbase = 0
        
    def peek(self, loc):
        return self.instr[loc] if 0 <= loc < len(self.instr) else 0
        
    def process_params(self, opmode):
        return [*zip(*[((z:=self.peek(self.ptr+1+i)), self.peek(z)) if j=='0' 
                       else ((z:=self.ptr+1+i), self.peek(z)) if j=='1'
                       else ((z:=self.relbase+self.peek(self.ptr+1+i)), self.peek(z)) if j=='2'
                       else (None, None)
                       for i,j in enumerate((str(opmode//100)[::-1]+'000')[:3])])]
        
    def maybe_extend_memory(self, address):
        if address >= (z:=len(self.instr)):
            self.instr.extend([0]*(address-z+1))
    
    def do_add(self, addr, val):
        if self.verbose:  print(f"Ptr={self.ptr:2d}:  Set address {addr[2]} to {val[0]} + {val[1]}")
        self.maybe_extend_memory(addr[2])
        self.instr[addr[2]] = val[0] + val[1]
        self.ptr += 4

    def do_mult(self, addr, val):
        if self.verbose:  print(f"Ptr={self.ptr:2d}:  Set address {addr[2]} to {val[0]} * {val[1]}")
        self.maybe_extend_memory(addr[2])
        self.instr[addr[2]] = val[0] * val[1]
        self.ptr += 4

    def do_input(self, addr, val):
        if self.input_val:
            if self.verbose:  print(f"Ptr={self.ptr:2d}:  Set address {addr[0]} from INPUT to {self.input_val[0]}")
            self.maybe_extend_memory(addr[0])
            self.instr[addr[0]] = self.input_val.pop(0)
            self.ptr += 2
        else:
            if self.verbose:  print(f"Ptr={self.ptr:2d}:  Nothing in INPUT; waiting...")
    
    def do_output(self, addr, val):
        if self.verbose:  print(f"Ptr={self.ptr:2d}:  OUTPUT value {val[0]}")
        self.output += [val[0]]
        self.ptr += 2
        
    def do_jump_if_true(self, addr, val):
        if self.verbose:  print(f"Ptr={self.ptr:2d}:  Jump to {val[1]} if {val[0]} != 0")
        if val[0]:
            self.ptr = val[1]
        else:
            self.ptr += 3

    def do_jump_if_false(self, addr, val):
        if self.verbose:  print(f"Ptr={self.ptr:2d}:  Jump to {val[1]} if {val[0]} == 0")
        if val[0] == 0:
            self.ptr = val[1]
        else:
            self.ptr += 3

    def do_less_than(self, addr, val):
        if self.verbose:  print(f"Ptr={self.ptr:2d}:  Set address {addr[2]} to 1 if {val[0]} < {val[1]} else 0")
        self.maybe_extend_memory(addr[2])
        self.instr[addr[2]] = int(val[0] < val[1])
        self.ptr += 4

    def do_equals(self, addr, val):
        if self.verbose:  print(f"Ptr={self.ptr:2d}:  Set address {addr[2]} to 1 if {val[0]} == {val[1]} else 0")
        self.maybe_extend_memory(addr[2])
        self.instr[addr[2]] = int(val[0] == val[1])
        self.ptr += 4

    def do_adjust_relbase(self, addr, val):
        if self.verbose:  print(f"Ptr={self.ptr:2d}:  Adjust relbase from {self.relbase} by {val[0]} to {self.relbase+val[0]}")
        self.relbase += val[0]
        self.ptr += 2

    def do_exec(self, reset=True):
        if reset:  self.reset()
        while True:
            opmode = self.instr[self.ptr]
            opcode = opmode % 100
            if opcode == 99:
                if self.verbose:  print("STOP")
                break
            self.ops[opcode](*self.process_params(opmode))
