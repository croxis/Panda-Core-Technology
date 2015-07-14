#version 130

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

void main(void)
{

   vec4 textureColor = texture2D(colorTexture, texCoords);
   vec4 nightColor = texture2D(nightTesture, texCoords);
   vec4 specColor = texture2D(glossTexture, texCoords);
   vec3 normalDirection = normalize(varyingNormalDirection);
   vec3 viewDirection = normalize(-position); 
   vec3 lightDirection = normalize(gl_LightSource[0].position.xyz - position); 
   vec3 diffuseReflection = vec3(gl_LightSource[0].diffuse) * vec3(textureColor)
                           * max(0.0, dot(normalDirection, lightDirection));

   vec3 specularReflection = vec3(0.0, 0.0, 0.0);
   if (dot(normalDirection, lightDirection) >= 0.0) // light source on the wrong side?
    {
        specularReflection = vec3(gl_LightSource[0].specular) * vec3(gl_FrontMaterial.specular) * specColor.a
        * pow(max(0.0, dot(reflect(-lightDirection, normalDirection), viewDirection)), gl_FrontMaterial.shininess);
    }
   float levelOfLighting = max(0.0, dot(normalDirection, lightDirection)) + 0.5;
   //0.5 is added as otherwise too much of night shines through.
   //Later I want to use as a nighttime glowmap instead

   vec4 dayColor = vec4(diffuseReflection + specularReflection, 1.0);

   gl_FragColor = mix(nightColor, dayColor, levelOfLighting);
   //gl_FragColor = textureColor;
   //gl_FragColor = vec4(1, 1, 1, 1);
}
