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

from motor_params import MotorParams

def float2uint(x, x_min, x_max, bits):
        span = x_max - x_min
        offset = x_min
        return int((x-offset)*(int((1<<bits)-1))/span)

def uint2float(x, x_min, x_max, bits):
    span = x_max - x_min
    offset = x_min
    return float(x*span/((1<<bits)-1) + offset)

def unpack_reply(rx_data, params:MotorParams):
        # /// 0: id
        # /// 1: [position[15-8]]
        # /// 2: [position[7-0]]
        # /// 3: [velocity[11-4]]
        # /// 4: [velocity[3-0], current[11-8]]
        # /// 5: [current[7-0]]
        P_MIN = params.p_des.min_value
        P_MAX = params.p_des.max_value
        V_MIN = params.v_des.min_value
        V_MAX = params.v_des.max_value
        I_MAX = params.i_ff.max_value
        p_bits = params.p_des.bits
        v_bits = params.v_des.bits
        i_bits = params.i_ff.bits
        if len(rx_data) == 6:
            id = rx_data[0]
            p = rx_data[1]<<8 | rx_data[2]
            v = rx_data[3]<<4 | rx_data[4]>>4
            i = (rx_data[4]&0xF)<<8 | rx_data[5]
            
            p = uint2float(p, P_MIN, P_MAX, p_bits)
            v = uint2float(v, V_MIN, V_MAX, v_bits)
            i = uint2float(i, -I_MAX, I_MAX, i_bits)
            return [id, p, v, i]
        else:
            return None