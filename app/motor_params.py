"""MIT License

Copyright (c) 2023 Nipun Dhananjaya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from dataclasses import dataclass
import dataclasses
# from dataclasses_json import dataclass_json
import json
import sys, os


basedir = os.path.dirname(__file__)


# @dataclass_json
@dataclass
class _Params:
    cmd:float
    bits:int
    min_value:float
    max_value:float
    def get_uint_cmd_value(self):
        span = self.max_value - self.min_value
        offset = self.min_value
        return int((self.cmd - offset)*(int((1<<self.bits)-1))/span)
    def set_cmd_value_from_uint(self, uint):
        span = self.max_value - self.min_value
        offset = self.min_value
        self.cmd = float(uint*span/((1<<self.bits)-1) + offset)
    def get_uint_max_value(self):
        return (1<<self.bits) -1



# @dataclass_json
@dataclass
class MotorParams:
    p_des:_Params
    v_des:_Params
    kp:_Params
    kd:_Params
    i_ff:_Params 

    def __init__(self):
        self.p_des:_Params = _Params(cmd=0, bits=16, min_value=-12.5, max_value=12.5)
        self.v_des:_Params = _Params(cmd=0, bits=12, min_value=-65, max_value=65)
        self.kp:_Params    = _Params(cmd=0, bits=12, min_value=0, max_value=500)
        self.kd:_Params    = _Params(cmd=0, bits=12, min_value=0, max_value=5)
        self.i_ff:_Params  = _Params(cmd=0, bits=12, min_value=-20, max_value=20)

    def _get_asdict(self):
        return dataclasses.asdict(self)
    
    def _save_data(self, path:str=""):
        with open(os.path.join(basedir, "motor_params.json"), "w") as f:
            param_dict = self._get_asdict()
            param_dict["p_des"]["cmd"] = 0
            json.dump(param_dict, f)

    def _load_data(self, path:str=""):
        try:
            with open(os.path.join(basedir, "motor_params.json"), "r") as f:
                data = json.load(f)
                self.p_des.cmd = data['p_des']['cmd']
                self.p_des.bits = data['p_des']['bits']
                self.p_des.min_value = data['p_des']['min_value']
                self.p_des.max_value = data['p_des']['max_value']
                self.v_des.cmd = data['v_des']['cmd']
                self.v_des.bits = data['v_des']['bits']
                self.v_des.min_value = data['v_des']['min_value']
                self.v_des.max_value = data['v_des']['max_value']
                self.kp.cmd = data['kp']['cmd']
                self.kp.bits = data['kp']['bits']
                self.kp.min_value = data['kp']['min_value']
                self.kp.max_value = data['kp']['max_value']
                self.kd.cmd = data['kd']['cmd']
                self.kd.bits = data['kd']['bits']
                self.kd.min_value = data['kd']['min_value']
                self.kd.max_value = data['kd']['max_value']
                self.i_ff.cmd = data['i_ff']['cmd']
                self.i_ff.bits = data['i_ff']['bits']
                self.i_ff.min_value = data['i_ff']['min_value']
                self.i_ff.max_value = data['i_ff']['max_value']
        except Exception as e:
            print(e)
