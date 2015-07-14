// Rayleigh
const float HR = 8.0;
const vec3 betaR = vec3(5.8e-3, 1.35e-2, 3.31e-2);

// Mie
// DEFAULT
const float HM = 1.2;
const vec3 betaMSca = vec3(4e-3);
const vec3 betaMEx = betaMSca / 0.9;
const float mieG = 0.8;
// CLEAR SKY
/*const float HM = 1.2;
const vec3 betaMSca = vec3(20e-3);
const vec3 betaMEx = betaMSca / 0.9;
const float mieG = 0.76;*/
// PARTLY CLOUDY
/*const float HM = 3.0;
const vec3 betaMSca = vec3(3e-3);
const vec3 betaMEx = betaMSca / 0.9;
const float mieG = 0.65;*/

// ----------------------------------------------------------------------------
// NUMERICAL INTEGRATION PARAMETERS
// ----------------------------------------------------------------------------

const int TRANSMITTANCE_INTEGRAL_SAMPLES = 500;
const int INSCATTER_INTEGRAL_SAMPLES = 50;
const int IRRADIANCE_INTEGRAL_SAMPLES = 32;
const int INSCATTER_SPHERICAL_INTEGRAL_SAMPLES = 16;

const int TRANSMITTANCE_W = 256;
const int TRANSMITTANCE_H = 64;

const float M_PI = 3.141592657;

in float Rg;
in float RL;
in float Rt;

#define TRANSMITTANCE_NON_LINEAR

// nearest intersection of ray r,mu with ground or top atmosphere boundary
// mu=cos(ray zenith angle at ray origin)
float limit(float r, float mu) {
    float dout = -r * mu + sqrt(r * r * (mu * mu - 1.0) + RL * RL);
    float delta2 = r * r * (mu * mu - 1.0) + Rg * Rg;
    if (delta2 >= 0.0) {
        float din = -r * mu - sqrt(delta2);
        if (din >= 0.0) {
            dout = min(dout, din);
        }
    }
    return dout;
}

void getTransmittanceRMu(out float r, out float muS) {
    r = gl_FragCoord.y / float(TRANSMITTANCE_H);
    muS = gl_FragCoord.x / float(TRANSMITTANCE_W);
//#ifdef TRANSMITTANCE_NON_LINEAR
    r = Rg + (r * r) * (Rt - Rg);
//    muS = -0.15 + tan(1.5 * muS) / tan(1.5) * (1.0 + 0.15);
//#else
//    r = Rg + r * (Rt - Rg);
//    muS = -0.15 + muS * (1.0 + 0.15);
//#endif
}


//float opticalDepth(float H, float r, float mu)
//{
//    float result = 0.0;
//    float dx = limit(r, mu) / float(TRANSMITTANCE_INTEGRAL_SAMPLES);
//    float xi = 0.0;
//    float yi = exp(-(r - Rg) / H);
 //   for (int i = 1; i <= TRANSMITTANCE_INTEGRAL_SAMPLES; ++i) {
  //      float xj = float(i) * dx;
   //     float yj = exp(-(sqrt(r * r + xj * xj + 2.0 * xj * r * mu) - Rg) / H);
     //   result += (yi + yj) / 2.0 * dx;
        //xi = xj;
//        yi = yj;
//    }
//    return mu < -sqrt(1.0 - (Rg / r) * (Rg / r)) ? 1e9 : result;
//}

float opticalDepth(float H, float r, float mu)
{
    float cosHorizon = -sqrt(1.0 - ((Rg*Rg)/(r*r)));
    if (mu < cosHorizon)
        return 1e9;
    float totalDensity = 0.0;
    float dx = limit(r, mu) / float(TRANSMITTANCE_INTEGRAL_SAMPLES);
    float y_j = exp(-(r-Rg)/H);
    for (int i = 1; i<=TRANSMITTANCE_INTEGRAL_SAMPLES; ++i)
    {
        float x_i = float(i)*dx;
        float alt_i = sqrt(r*r + x_i* x_i + 2.0*x_i*r*mu);
        float y_i = exp(-(alt_i - Rg)/H);
        totalDensity += (y_j+ y_i)/2.0*dx;
        y_j = y_i;
    }
    return totalDensity;
}

void main()
{  
    float r, muS;
    getTransmittanceRMu(r, muS);
    // calculates extinction factor of given altitude and view direction
    vec3 depth = betaR * opticalDepth(HR, r, muS) + betaMEx * opticalDepth(HM, r, muS);
    gl_FragColor = vec4(exp(-depth), 0.0);
   // gl_FragColor = vec4(r, 0.0, 0.0, 1.0);
    //gl_FragColor = vec4(exp(betaR * densityOverPath(HR, alt, mu)), 1.0);
    //gl_FragColor = vec4(1.0, 0.0, 1.0, 1.0);
}

void main_bruneton()
{  
    float r, muS;
    getTransmittanceRMu(r, muS);
    // calculates extinction factor of given altitude and view direction
    vec3 depth = betaR * opticalDepth(HR, r, muS) + betaMEx * opticalDepth(HM, r, muS);
    //gl_FragColor = vec4(exp(-depth), 0.0);
    gl_FragColor = vec4(r, 0.0, 0.0, 1.0);
    //gl_FragColor = vec4(exp(betaR * densityOverPath(HR, alt, mu)), 1.0);
    //gl_FragColor = vec4(1.0, 0.0, 1.0, 1.0);
}
