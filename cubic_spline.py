import numpy as np

class BandMatrix:
    """
    """
    def __init__(self, _m_middle, _m_upper, _m_lower, _rhs):
        self.m_middle = _m_middle
        self.m_upper = _m_upper
        self.m_lower = _m_lower
        self.rhs = _rhs

    def lu_decompose(self):
        """return the lower matrix and upper matrix through decompose a band matrix

        Args:

        Returns:
            a lower band list and a middle band list
            For example:

            L1=1 0 0 0
            L2=bb1 1 0 0
            L3=0 bb2 1 0
            L4=0 0 bb3 1

            U1=dd1 a1 0 0
            U2=0 dd2 a2 0
            U3=0 0 dd3 a3
            U4=0 0 0 dd4

            bb list and dd list will be returned

        Raises:
            **ValueError**: An error occurred due to matrix diagonal line element is 0
        """
        n = len(self.m_middle)
        low_bb = []
        low_bb.append(0)
        mid_dd = []
        mid_dd.append(self.m_middle[0])
        for i in range(1, n):
            if mid_dd[i - 1] != 0.0:
                low_bb.append(float(self.m_lower[i]) / mid_dd[i - 1])
            else:
                print('matrix A[i][i] should not equal to 0')
                break
            mid_dd.append(float(self.m_middle[i] - float(low_bb[i] * self.m_upper[i - 1])))
        return low_bb, mid_dd

    def l_solve(self):
        """
        solve Ly=rhs

        """
        n = len(self.m_lower)
        y = []
        y.append(self.rhs[0])
        for i in range(1, n):
            sum = 0
            sum = sum + self.m_lower[i] * self.rhs[i - 1]
            self.rhs[i] = self.rhs[i] - sum
            y.append(self.rhs[i])
        return y

    def u_solve(self):
        """
        solve Ux=y

        """
        n = len(self.m_middle)
        y = []
        for i in range(0, n):
            y.append(0)

        y[n - 1] = float(self.rhs[n - 1] / self.m_middle[n - 1])
        self.rhs[n - 1] = y[n - 1]
        for i in range(n - 2, -1, -1):
            sum = 0
            sum = sum + self.m_upper[i] * self.rhs[i + 1]
            self.rhs[i] = float(self.rhs[i] - sum) / self.m_middle[i]
            y[i] = self.rhs[i]
        return y

    def lu_solve(self):
        self.m_lower, self.m_middle = self.lu_decompose()
        self.rhs = self.l_solve()
        x = self.u_solve()
        return x


class Spline:
    """
    """
    def __init__(self,_x, _y,xi):
        self.x = _x
        self.y = _y
        self.m_a=[]
        self.m_b=[]
        self.m_c=[]
        self.m_left='second_deriv'
        self.m_left_value = 0.0
        self.m_right = 'second_deriv'
        self.m_right_value = 0.0
        m=len(xi)
        self.x_ext=np.zeros(m)
        self.ma_ext=np.zeros(m)
        self.mb_ext=np.zeros(m)
        self.mc_ext=np.zeros(m)
        self.y_ext=np.zeros(m)


    def spline_setpoints(self):
        """return the coefficients for the interpolation calculation
           The detail math procedure is under: kluge.in-chemnitz.de/opensource/spline/

        Args:

        Return:
            there are five list will be updated:
            m_x, m_y, m_a, m_b, m_c
            it is the coefficients used to calculate the interpolation number.

        Raises:
            **ValueError**: An error occurred when:
            1. x list is not in sequence
            2. x list and y list are not in same length
            3. x list is too short that only have less than 3 number of elements
        """
        n = len(self.x)
        for i in range(0, n - 1):
            if self.x[i] > self.x[i + 1]:
                print('error: x not in sequence')
                conti_x = 0
            else:
                conti_x = 1
        if len(self.x) != len(self.y):
            print('error: x and y are not same length')
            conti_x = 0
        elif len(self.x) < 3:
            print('error: data x not long enough')
            conti_x = 0

        if conti_x == 1:
            Amiddle = []
            Aupper = []
            Alower = []
            rhs = []
            for i in range(0, n):
                Amiddle.append(0)
                Aupper.append(0)
                Alower.append(0)
                rhs.append(0)

            for i in range(1, n - 1):
                Alower[i] = (self.x[i] - self.x[i - 1]) / 3.0
                Amiddle[i] = (self.x[i + 1] - self.x[i - 1]) * 2.0 / 3.0
                Aupper[i] = (self.x[i + 1] - self.x[i]) / 3.0
                rhs[i] = ((self.y[i + 1] - self.y[i]) / (self.x[i + 1] - self.x[i]) -
                         (self.y[i] - self.y[i - 1]) / (self.x[i] - self.x[i - 1]))

            if self.m_left == 'second_deriv':
                Amiddle[0] = 2.0
                Aupper[0] = 0.0
                rhs[0] = self.m_left_value;
            elif self.m_left == 'first_deriv':
                Aupper[0] = 2.0 * (self.x[1] - self.x[0])
                Amiddle[0] = 1.0 * (self.x[1] - self.x[0])
                rhs[0] = 3.0 * ((self.y[1] - self.y[0]) / (self.x[1] - self.x[0]) - self.m_left_value)
            else:
                return None
            if self.m_right == 'second_deriv':
                Amiddle[n - 1] = 2.0
                Alower[n - 1] = 0.0
                rhs[n - 1] = self.m_right_value
            elif self.m_right == 'first_deriv':
                Amiddle[n - 1] = 2.0 * (self.x[n - 1] - self.x[n - 2])
                Alower[n - 2] = 1.0 * (self.x[n - 1] - self.x[n - 2])
                rhs[n - 1] = 3.0 * (self.m_right_value - (self.y[n - 1] - self.y[n - 2])
                                    / (self.x[n - 1] - self.x[n - 2]))
            else:
                return None

            bm = BandMatrix(Amiddle, Aupper, Alower, rhs)
            self.m_b = bm.lu_solve()

            for i in range(0, n):
                self.m_a.append(0)
                self.m_c.append(0)
            for i in range(0, n - 1):
                self.m_a[i] = 1.0 / 3.0 * (self.m_b[i + 1] - self.m_b[i]) / (self.x[i + 1] - self.x[i])
                self.m_c[i] = ((self.y[i + 1] - self.y[i]) / (self.x[i + 1] - self.x[i]) -
                         1.0 / 3.0 * (2.0 * self.m_b[i] + self.m_b[i + 1]) * (self.x[i + 1] - self.x[i]))

            h = self.x[n - 1] - self.x[n - 2]
            self.m_a[n - 1] = 0.0
            self.m_c[n - 1] = 3.0 * self.m_a[n - 2] * h * h + 2.0 * self.m_b[n - 2] * h + self.m_c[n - 2]
            self.m_b[n - 1] = 0.0
        else:
            print('input is wrong!!')
            return None


    def spline(self, xi):
        """return the interpolation number
            the result of this library is compared against alglib(www.algib.net/download.php)
            Interpolation results are identical but extrapolation differs, as this library is
            designed to extrapolate linearly.
            The detail math procedure is under: kluge.in-chemnitz.de/opensource/spline/

        Args:
            **xi**(number): a float type number list, to calculate the interpolation y value on this x point

        Return:
            A float type interpolation number array will be returned

        Raises:
        """
        m = len(xi)
        idx = np.digitize(xi, self.x)
        mv = np.maximum(idx-1 , np.zeros(m,dtype=np.int))
        self.x_ext = np.take(self.x, mv)
        self.mb_ext = np.take(self.m_b, mv)
        self.mc_ext = np.take(self.m_c, mv)
        self.y_ext = np.take(self.y, mv)
        self.ma_ext = np.take(self.m_a, mv)

        for i in xrange(0, m):
            if xi[i] >= self.x[0]:
                break
            else:
                self.ma_ext[i] = 0

        h = np.array(xi) - self.x_ext
        interpol = ((self.ma_ext * h + self.mb_ext) * h + self.mc_ext) * h + self.y_ext
        return interpol