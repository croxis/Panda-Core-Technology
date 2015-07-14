#version 130

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
//uniform mat4 p3d_ModelViewMatrix; BROKEN!
out vec2 texCoords;

in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
//in mat3 p3d_NormalMatrix;
uniform mat4 p3d_ModelViewMatrixInverseTranspose;
out vec3 varyingNormalDirection;
out vec3 position;  // position of the vertex (and fragment) in world space



void main(void) {
    // Standard mode
    //gl_Position = p3d_ModelViewProjectionMatrix * gl_Vertex;

    vec4 v = p3d_Vertex;

    //By adding 1 to z we move our grid to make a cube.
    //We do 1 instead of 0.5 to make all the math easy.
    v.z += 1.0;
    //vec4 vertex = v;//Shows it as a cube

    vec4 vertex = vec4(normalize(v.xyz), v.w);

    //While this simple normalizing works it causes some distortion near the edges
    //While less distoration than a standard sphere there are more ideal solutions
    //Some cubemapping software, such as PLanettool 
    //http://wiki.alioth.net/index.php/Planettool
    //compensates for said distortions within the texture. I use this tool. Therefore...
    gl_Position = p3d_ModelViewProjectionMatrix * vertex;
    
    //The normalization creates almost no edge distortion in vertex placement
    //Use when using unmodified flat textures
    //Proof: http://mathproofs.blogspot.com/2005/07/mapping-cube-to-sphere.html
    //float x = test.x;
    //float y = test.y;
    //float z = test.z;
    //test.x *= sqrt(1.0 - y * y * 0.5 - z * z * 0.5 + y * y * z * z / 3.0);
    //test.y *= sqrt(1.0 - z * z * 0.5 - x * x * 0.5 + z * z * x * x / 3.0);
    //test.z *= sqrt(1.0 - x * x * 0.5 - y * y * 0.5 + x * x * y * y / 3.0);
    //gl_Position = p3d_ModelViewProjectionMatrix * test;

    //v = vec3(gl_ModelViewMatrix * vertex); 
    //N = normalize(gl_NormalMatrix * vertex.xyz);
    texCoords = vec2(p3d_MultiTexCoord0);
    //varyingNormalDirection = normalize(p3d_NormalMatrix * v.xyz);
    //varyingNormalDirection = normalize(gl_NormalMatrix * v.xyz);
    varyingNormalDirection = normalize(mat3(gl_ModelViewMatrixInverseTranspose) * v.xyz);
    //position = vec3(gl_ModelViewMatrix * v); 
    position = vec3(p3d_ModelViewMatrix * v); 

}