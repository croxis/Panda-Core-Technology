varying vec4 position;
varying vec4 true_position;
varying vec2 texture_coordinate;

void main() {
    //position = 0.5 * (gl_Vertex + vec4(1.0, 1.0, 1.0, 0.0));
    position = gl_Vertex * 0.3;
    true_position = gl_Vertex;
  //gl_Position = ftransform();
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
  texture_coordinate = vec2(gl_MultiTexCoord0);
  gl_TexCoord[0] = gl_MultiTexCoord0;
}