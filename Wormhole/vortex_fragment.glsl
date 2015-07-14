varying vec4 position;
varying vec4 true_position;

uniform float time;
uniform vec2 mouse;

vec2 Offset;
vec2 Scale=vec2(0.1,0.1);
float Saturation = 0.1; // 0 - 1;

float field(in vec3 p) {
    float strength = 7. + .03 * log(1.e-6 );
    float accum = 0.;
    float prev = 0.;
    float tw = 0.;
    for (int i = 0; i < 32; ++i) {
        float mag = dot(p, p);
        p = abs(p) / mag + vec3(-.5, -.4, -1.5);
        float w = exp(-float(i) / 7.);
        accum += w * exp(-strength * pow(abs(mag - prev), 2.3));
        tw += w;
        prev = mag;
    }
    return max(0., 5. * accum / tw - .7);
}

vec3 lungth(vec2 x,vec3 c){
       return vec3(length(x+c.r),length(x+c.g),length(c.b));
}

void main() {
    float th = atan(position.y, position.x) / (2.0 * 3.1415926);
    float dd = length(position) + 0.005;
    float d = 0.5 / dd + time;
    
    vec2 x = gl_FragCoord.xy;
    vec3 c2=vec3(0,0,0);
    x+=sin(x.yx*sqrt(vec2(13,9)))/1.;
    c2=lungth(sin(x*sqrt(vec2(33,43))),vec3(5,6,7)*Saturation * d);
    x+=sin(x.yx*sqrt(vec2(73,53)))/5.;
    c2=2.*lungth(sin(time+x*sqrt(vec2(33.,23.))),c2/9.);
    x+=sin(x.yx*sqrt(vec2(93,73)))/3.;
    c2=lungth(sin(x*sqrt(vec2(13.,1.))),c2/2.0);
    c2=.5+.5*sin(c2*8.);
    
    vec3 uv = vec3(th + d, th - d, th + sin(d) * 0.0);
    float a = 0.5 + cos(uv.x * 3.1415926 * 2.0) * 0.5;
    float b = 0.5 + cos(uv.y * 3.1415926 * 2.0) * 0.5;
    float c = 0.5 + cos(uv.z * 3.1415926 * 6.0) * 0.5;
    //vec3 color;
    vec3 color =    mix(vec3(0.1, 0.5, 0.5),    vec3(0.1, 0.1, 0.2),  pow(a, 0.2)) * 3.;
    //color +=    mix(vec3(0.8, 0.2, 1.0),    vec3(0.1, 0.1, 0.2),  pow(b, 0.1)) * 0.75;
    //color +=    mix(c2,             vec3(0.1, 0.2, 0.2),  pow(c, 0.1)) * 0.75;

    //https://www.shadertoy.com/view/lslGWr
    vec2 uv_frac = 2. * gl_FragCoord.xy / true_position.xy - 1;
    vec3 p = vec3(uv_frac / 4., 0) + vec3(1., -1.3, 0.);
    p += .2 * vec3(0., sin(time/64.),  sin(time / 64.));
    float t = field(p);
    float v = (1. - exp((abs(uv_frac.x) - 1.) * 6.)) * (1. - exp((abs(uv_frac.y) - 1.) * 6.));
    vec4 frac_color = mix(.4, 1., v) * vec4(1.8 * t * t * t, 1.4 * t * t, t, 1.0) ;


    
    
    //gl_FragColor = frac_color;
    //gl_FragColor = vec4(color * dd, 1.0) + frac_color;
    //gl_FragColor = vec4( (color * dd), 0.5) + frac_color;
}