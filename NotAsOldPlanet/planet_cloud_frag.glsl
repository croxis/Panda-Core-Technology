#version 130

// Procedural planet generator
// Copyright (C) 2012  Vladimir Romanuk
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
// 1. Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in the
//    documentation and/or other materials provided with the distribution.
// 3. Neither the name of the copyright holders nor the names of its
//    contributors may be used to endorse or promote products derived from
//    this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION)HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
// THE POSSIBILITY OF SUCH DAMAGE.


uniform sampler2D colorTexture;
uniform sampler2D nightTesture;
uniform sampler2D glossTexture;
in vec2 texCoords;

//varying vec3 N;
//varying vec3 v;    

uniform mat4 plight_plight0_rel_view;

in vec3 position;  // position of the vertex (and fragment) in world space
in vec3 varyingNormalDirection;  // surface normal vector in world space
uniform mat4 p3d_frontMaterial;
//varying out vec4 FragColor;

uniform sampler3D   NoiseSampler;       // precomputed noise texture

uniform vec3    Randomize;      // Randomize
uniform vec4    faceParams;     // (x0,             y0,             size,                   face)
uniform vec4    scaleParams;    // (offsU,          offsV,          scale,                  tidalLock)
uniform vec4    cloudsParams1;  // (cloudsFreq,     cloudsOctaves,  twistZones,             twistMagn)
uniform vec4    cloudsParams2;  // (cloudsLayer,    cloudsNLayers,  cloudsStyle,            cloudsCoverage)
uniform vec4    cycloneParams;  // (cycloneMagn,    cycloneFreq,    sqrt(cycloneDensity),   cycloneOctaves)

uniform sampler1D   CloudsColorTable;   // clouds color table

const float pi = 3.14159265358;

float   noiseOctaves;
float   noiseLacunarity  = 2.218281828459;
float   noiseH           = 0.5;
float   noiseOffset      = 0.8;
float   noiseRidgeSmooth = 0.0001;

#define     tidalLock           scaleParams.w
#define     cloudsFreq          cloudsParams1.x
#define     cloudsOctaves       cloudsParams1.y
#define     twistZones          cloudsParams1.z
#define     twistMagn           cloudsParams1.w
#define     cloudsLayer         cloudsParams2.x
#define     cloudsNLayers       cloudsParams2.y
#define     cloudsStyle         cloudsParams2.z
#define     cloudsCoverage      cloudsParams2.w
#define     cycloneMagn         cycloneParams.x
#define     cycloneFreq         cycloneParams.y
#define     cycloneSqrtDensity  cycloneParams.z
#define     cycloneOctaves      cycloneParams.w

#define NOISE_TEX_3D_SIZE   64.0
#define PACKED_NORMALS      1


#define NoiseNearestU    (p)    texture3D(NoiseSampler, p).r
#define NoiseNearestUVec3(p)    texture3D(NoiseSampler, p).rgb
#define NoiseNearestUVec4(p)    texture3D(NoiseSampler, p)


// Generates 3 random numbers for each of the 8 cell corners
void FastHash3D(vec3 gridcell,
                out vec4 lowz_hash_0,
                out vec4 lowz_hash_1,
                out vec4 lowz_hash_2,
                out vec4 highz_hash_0,
                out vec4 highz_hash_1,
                out vec4 highz_hash_2)
{
    // gridcell is assumed to be an integer coordinate
    const vec2  OFFSET = vec2(50.0, 161.0);
    const float DOMAIN = 69.0;
    const vec3  SOMELARGEFLOATS = vec3(635.298681, 682.357502, 668.926525);
    const vec3  ZINC = vec3(48.500388, 65.294118, 63.934599);

    //  truncate the domain
    gridcell.xyz = gridcell.xyz - floor(gridcell.xyz * (1.0 / DOMAIN))* DOMAIN;
    vec3 gridcell_inc1 = mix(gridcell + vec3(1.0), vec3(0.0), greaterThan(gridcell, vec3(DOMAIN - 1.5)));

    //  calculate the noise
    vec4 P = vec4(gridcell.xy, gridcell_inc1.xy) + OFFSET.xyxy;
    P *= P;
    P = P.xzxz * P.yyww;
    lowz_hash_2.xyzw = vec4(1.0)/ (SOMELARGEFLOATS.xyzx + vec2(gridcell.z, gridcell_inc1.z).xxxy * ZINC.xyzx);
    highz_hash_2.xy  = vec2(1.0)/ (SOMELARGEFLOATS.yz + gridcell_inc1.zz * ZINC.yz);
    lowz_hash_0  = fract(P *  lowz_hash_2.xxxx);
    highz_hash_0 = fract(P *  lowz_hash_2.wwww);
    lowz_hash_1  = fract(P *  lowz_hash_2.yyyy);
    highz_hash_1 = fract(P * highz_hash_2.xxxx);
    lowz_hash_2  = fract(P *  lowz_hash_2.zzzz);
    highz_hash_2 = fract(P * highz_hash_2.yyyy);
}

//-----------------------------------------------------------------------------
void FastHash3D(vec3 gridcell, out vec4 lowz_hash, out vec4 highz_hash)
{
  // g ridcell is assumed to be an integer coordinate
  const vec2 OFFSET = vec2(50.0, 161.0);
  const float DOMAIN = 69.0;
  const float SOMELARGEFLOAT = 635.298681;
  const float ZINC = 48.500388;

  //  truncate the domain
  gridcell.xyz = gridcell.xyz - floor(gridcell.xyz * (1.0 / DOMAIN)) * DOMAIN;
  vec3 gridcell_inc1 = step(gridcell, vec3(DOMAIN - 1.5)) * (gridcell + 1.0);

  //  calculate the noise
  vec4 P = vec4(gridcell.xy, gridcell_inc1.xy) + OFFSET.xyxy;
  P *= P;
  P = P.xzxz * P.yyww;
  highz_hash.xy = vec2(1.0 / (SOMELARGEFLOAT + vec2(gridcell.z, gridcell_inc1.z) * ZINC));
  lowz_hash  = fract(P * highz_hash.xxxx );
  highz_hash = fract(P * highz_hash.yyyy );
}

//-----------------------------------------------------------------------------
vec3 InterpC2(vec3 x) { return x * x * x * (x * (x * 6.0 - 15.0) + 10.0); }
//-----------------------------------------------------------------------------


// 3D Perlin noise without lookup textures
float   Noise(vec3 p)
{
    // Establish our grid cell and unit position
    vec3 Pi = floor(p);
    vec3 Pf = p - Pi;
    vec3 Pf_min1 = Pf - 1.0;

#if 1
    // Classic noise. Requires 3 random values per point.
    // With an efficent hash function will run faster than improved noise.

    // Calculate the hash
    vec4 hashx0, hashy0, hashz0, hashx1, hashy1, hashz1;
    FastHash3D(Pi, hashx0, hashy0, hashz0, hashx1, hashy1, hashz1);

    // Calculate the gradients
    const vec4 C = vec4(0.49999);
    vec4 grad_x0 = hashx0 - C;
    vec4 grad_y0 = hashy0 - C;
    vec4 grad_z0 = hashz0 - C;
    vec4 grad_x1 = hashx1 - C;
    vec4 grad_y1 = hashy1 - C;
    vec4 grad_z1 = hashz1 - C;
    vec4 grad_results_0 = inversesqrt(grad_x0 * grad_x0 + grad_y0 * grad_y0 + grad_z0 * grad_z0)* (vec2(Pf.x, Pf_min1.x).xyxy * grad_x0 + vec2(Pf.y, Pf_min1.y).xxyy * grad_y0 + Pf.zzzz * grad_z0);
    vec4 grad_results_1 = inversesqrt(grad_x1 * grad_x1 + grad_y1 * grad_y1 + grad_z1 * grad_z1)* (vec2(Pf.x, Pf_min1.x).xyxy * grad_x1 + vec2(Pf.y, Pf_min1.y).xxyy * grad_y1 + Pf_min1.zzzz * grad_z1);

    // Classic Perlin Interpolation
    vec3 blend = InterpC2(Pf);
    vec4 res0 = mix(grad_results_0, grad_results_1, blend.z);
    vec2 res1 = mix(res0.xy, res0.zw, blend.y);
    float final = mix(res1.x, res1.y, blend.x);
    final *= 1.1547005383792515290182975610039; // (optionally) scale things to a strict -1.0->1.0 rang *= 1.0/sqrt(0.75)
    return final;
#else
    // Improved noise. Requires 1 random value per point.
    // Will run faster than classic noise if a slow hashing function is used.

    // Calculate the hash
    vec4 hash_lowz, hash_highz;
    FastHash3D(Pi, hash_lowz, hash_highz);

#if 0
    // This will implement Ken Perlins "improved" classic noise using the 12 mid-edge gradient points.
    // NOTE: mid-edge gradients give us a nice strict -1.0->1.0 range without additional scaling.
    // [1,1,0] [-1,1,0] [1,-1,0] [-1,-1,0]
    // [1,0,1] [-1,0,1] [1,0,-1] [-1,0,-1]
    // [0,1,1] [0,-1,1] [0,1,-1] [0,-1,-1]
    hash_lowz *= 3.0;
    vec4 grad_results_0_0 = mix(vec2(Pf.y, Pf_min1.y).xxyy, vec2(Pf.x, Pf_min1.x).xyxy, lessThan(hash_lowz, vec4(2.0)));
    vec4 grad_results_0_1 = mix(Pf.zzzz, vec2(Pf.y, Pf_min1.y).xxyy, lessThan(hash_lowz, vec4(1.0)));
    hash_lowz = fract(hash_lowz) - 0.5;
    vec4 grad_results_0 = grad_results_0_0 * sign(hash_lowz) + grad_results_0_1 * sign(abs(hash_lowz) - vec4(0.25));

    hash_highz *= 3.0;
    vec4 grad_results_1_0 = mix(vec2(Pf.y, Pf_min1.y).xxyy, vec2(Pf.x, Pf_min1.x).xyxy, lessThan(hash_highz, vec4(2.0)));
    vec4 grad_results_1_1 = mix(Pf_min1.zzzz, vec2(Pf.y, Pf_min1.y).xxyy, lessThan(hash_highz, vec4(1.0)));
    hash_highz = fract(hash_highz) - 0.5;
    vec4 grad_results_1 = grad_results_1_0 * sign(hash_highz) + grad_results_1_1 * sign(abs(hash_highz) - vec4(0.25));

    // Blend the gradients and return
    vec3 blend = InterpC2(Pf);
    vec4 res0 = mix(grad_results_0, grad_results_1, blend.z);
    vec2 res1 = mix(res0.xy, res0.zw, blend.y);
    return mix(res1.x, res1.y, blend.x);
#else
    // "Improved" noise using 8 corner gradients. Faster than the 12 mid-edge point method.
    // Ken mentions using diagonals like this can cause "clumping", but we'll live with that.
    // [1,1,1]  [-1,1,1]  [1,-1,1]  [-1,-1,1]
    // [1,1,-1] [-1,1,-1] [1,-1,-1] [-1,-1,-1]
    hash_lowz -= vec4(0.5);
    vec4 grad_results_0_0 = vec2(Pf.x, Pf_min1.x).xyxy * sign(hash_lowz);
    hash_lowz = abs(hash_lowz) - vec4(0.25);
    vec4 grad_results_0_1 = vec2(Pf.y, Pf_min1.y).xxyy * sign(hash_lowz);
    vec4 grad_results_0_2 = Pf.zzzz * sign(abs(hash_lowz) - vec4(0.125));
    vec4 grad_results_0 = grad_results_0_0 + grad_results_0_1 + grad_results_0_2;

    hash_highz -= vec4(0.5);
    vec4 grad_results_1_0 = vec2(Pf.x, Pf_min1.x).xyxy * sign(hash_highz);
    hash_highz = abs(hash_highz) - vec4(0.25);
    vec4 grad_results_1_1 = vec2(Pf.y, Pf_min1.y).xxyy * sign(hash_highz);
    vec4 grad_results_1_2 = Pf_min1.zzzz * sign(abs(hash_highz) - vec4(0.125));
    vec4 grad_results_1 = grad_results_1_0 + grad_results_1_1 + grad_results_1_2;

    // Blend the gradients and return
    vec3 blend = InterpC2(Pf);
    vec4 res0 = mix(grad_results_0, grad_results_1, blend.z);
    vec2 res1 = mix(res0.xy, res0.zw, blend.y);
    return mix(res1.x, res1.y, blend.x) * (2.0 / 3.0);   // (optionally) mult by (2.0/3.0)to scale to a strict -1.0->1.0 range
#endif

#endif
}

//-----------------------------------------------------------------------------

const vec3 vyd = vec3(3.33, 5.71, 1.96);
const vec3 vzd = vec3(7.77, 2.65, 4.37);
const vec3 vwd = vec3(1.13, 2.73, 6.37);
vec2    NoiseVec2    (vec3 p){ return vec2(Noise(p), Noise(p + vyd)); }
vec3    NoiseVec3    (vec3 p){ return vec3(Noise(p), Noise(p + vyd), Noise(p + vzd)); }
vec4    NoiseVec4    (vec3 p){ return vec4(Noise(p), Noise(p + vyd), Noise(p + vzd), Noise(p + vwd)); }
float   NoiseU       (vec3 p){ return Noise    (p)* 0.5 + 0.5; }
vec3    NoiseUVec3   (vec3 p){ return NoiseVec3(p)* 0.5 + vec3(0.5); }
vec4    NoiseUVec4   (vec3 p){ return NoiseVec4(p)* 0.5 + vec4(0.5); }

float   Fbm(vec3 point)
{
    float sum = 0.0;
    for (int i=0; i<noiseOctaves; ++i)
    {
        sum += Noise(point)* pow(noiseLacunarity, -noiseH*i);
        point *= noiseLacunarity;
    }
    return sum;
}

//-----------------------------------------------------------------------------

vec2    FbmVec2(vec3 point)
{
    vec2 sum = vec2(0.0);
    for (int i=0; i<noiseOctaves; ++i)
    {
        sum += NoiseVec2(point)* pow(noiseLacunarity, -noiseH*i);
        point *= noiseLacunarity;
    }
    return sum;
}

//-----------------------------------------------------------------------------

vec3    FbmVec3(vec3 point)
{
    vec3 sum = vec3(0.0);
    for (int i=0; i<noiseOctaves; ++i)
    {
        sum += NoiseVec3(point)* pow(noiseLacunarity, -noiseH*i);
        point *= noiseLacunarity;
    }
    return sum;
}

vec3    Rotate(float Angle, vec3 Axis, vec3 Vector)
{
    float cosa = cos(Angle);
    float sina = sin(Angle);
    float t = 1.0 - cosa;

    mat3x3 M = mat3x3(
        t * Axis.x * Axis.x + cosa,
        t * Axis.x * Axis.y - sina * Axis.z,
        t * Axis.x * Axis.z + sina * Axis.y,
        t * Axis.x * Axis.y + sina * Axis.z,
        t * Axis.y * Axis.y + cosa,
        t * Axis.y * Axis.z - sina * Axis.x,
        t * Axis.x * Axis.z - sina * Axis.y,
        t * Axis.y * Axis.z + sina * Axis.x,
        t * Axis.z * Axis.z + cosa);

    return Vector * M;
}

vec3    GetSurfacePoint()
{
    vec2 spherical;
    if (faceParams.w == 6.0)    // global
    {
        spherical.x = (gl_TexCoord[0].x * 2 - 0.5)* pi;
        spherical.y = (0.5 - gl_TexCoord[0].y) * pi;
        vec2 alpha = vec2(sin(spherical.x), cos(spherical.x));
        vec2 delta = vec2(sin(spherical.y), cos(spherical.y));
        return vec3(delta.y*alpha.x, delta.x, delta.y*alpha.y);
    }
    else                        // cubemap
    {
        spherical = gl_TexCoord[0].xy * faceParams.z + faceParams.xy;
        vec3 p = normalize(vec3(spherical, 1.0));
        if (faceParams.w == 0.0)
            return vec3( p.z, -p.y, -p.x);  // neg_x
        else if (faceParams.w == 1.0)
            return vec3(-p.z, -p.y,  p.x);  // pos_x
        else if (faceParams.w == 2.0)
            return vec3( p.x, -p.z, -p.y);  // neg_y
        else if (faceParams.w == 3.0)
            return vec3( p.x,  p.z,  p.y);  // pos_y
        else if (faceParams.w == 4.0)
            return vec3(-p.x, -p.y, -p.z);  // neg_z
        else
            return vec3( p.x, -p.y,  p.z);  // pos_z
    }
}

vec4    Cell2NoiseVec(vec3 p)
{
    vec3  cell = floor(p);
    vec3  offs = p - cell - vec3(0.5);
    vec3  pos;
    vec3  point = vec3(0.0);
    vec3  rnd;
    vec3  d;
    float distMin = 1.0e38;
    float dist;
    for (d.z=-1.0; d.z<1.0; d.z+=1.0)
    {
        for (d.y=-1.0; d.y<1.0; d.y+=1.0)
        {
            for (d.x=-1.0; d.x<1.0; d.x+=1.0)
            {
                rnd = NoiseNearestUVec4((cell + d)/ NOISE_TEX_3D_SIZE).xyz + d;
                pos = rnd - offs;
                dist = dot(pos, pos);
                if (distMin > dist)
                {
                    distMin = dist;
                    point = rnd;
                }
            }
        }
    }
    point = normalize(point + cell + vec3(0.5));
    return vec4(point, sqrt(distMin));
    //return vec4(point, sqrt(distMin));
}

float   HeightMapClouds(vec3 point)
{
    float zone = cos(point.y);
    float ang = zone * twistMagn;
    float weight = 1.0;
    float offset = 0.0;
    vec3  twistedPoint = point;

    // Compute cyclons
    vec3  cycloneCenter;
    float cycloneRadius = 1.0;
    float cycloneAmpl;
    if (tidalLock != 0.0)
    {
        cycloneCenter = vec3(0.0, 1.0, 0.0);
        cycloneRadius = length(cycloneCenter - point) / cycloneSqrtDensity;
        cycloneAmpl   = -cycloneMagn * sign(cycloneCenter.y);
    }
    else
    {
        vec4 cell = Cell2NoiseVec(point * cycloneFreq);
        cycloneCenter = cell.xyz;
        cycloneRadius = length(cycloneCenter - point) / cycloneSqrtDensity;
        cycloneAmpl   = 0.4*pi * sign(cycloneCenter.y);
    }
    if (cycloneRadius < 1.0)
    {
        float dist = 1.0 - cycloneRadius;
        float fi = mix(log(cycloneRadius), pow(dist, 3.0), cycloneRadius);
        twistedPoint = Rotate(cycloneAmpl*fi, cycloneCenter, point);
        if (cycloneRadius < 0.025)
            weight = 1.0 - pow(1.0 - cycloneRadius / 0.025, 2);
        else
            weight = 1.0;
        weight = weight * (1.0 + dist);
        //offset += 0.7 * dist;
    }

    // Compute Coriolis effect
    float sina = sin(ang);
    float cosa = cos(ang);
    twistedPoint = vec3(cosa*twistedPoint.x-sina*twistedPoint.z, twistedPoint.y, sina*twistedPoint.x+cosa*twistedPoint.z);
    twistedPoint = twistedPoint * cloudsFreq + Randomize;

    // Compute flow-like distortion
    noiseLacunarity = 3.0;
    noiseOctaves = 10;
    vec3  distort = FbmVec3(twistedPoint * 0.55) * 0.5;
    noiseOctaves = 6;
    float global = (Fbm(twistedPoint + distort) + 1.0) * 0.8;
    global = (global + offset) * weight;

    // Compute turbilence features
    noiseOctaves = cloudsOctaves;
    float turbulence = Fbm(point * 100.0 * cloudsFreq + Randomize) * 0.1;

    return  (global + turbulence * step(0.1, global) + cloudsCoverage);
}


#define     GetCloudsColor(height)          texture1D(CloudsColorTable, height)

void main(void)
{

   vec3 point = GetSurfacePoint();
   float height = HeightMapClouds(point);
   gl_FragColor = GetCloudsColor(height);
   gl_FragColor.g += 0.5;
   if (cloudsCoverage < 1.0)
        gl_FragColor *= height + cloudsCoverage;
   //gl_FragColor = vec4(1, 1, 1, 0.1);
}

