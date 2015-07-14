#version 420

#pragma include "Includes/Configuration.include"
#pragma include "Includes/Structures/VertexOutput.struct"
#pragma include "noise3D.glsl"


#extension GL_EXT_shader_image_load_store : enable


// Input from the vertex shader
layout(location=0) in VertexOutput vOutput;

// Texture Samplers
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform sampler2D p3d_Texture2;
uniform sampler2D p3d_Texture3;

layout(location=7) in vec4 position_in_object_coordinates;

#pragma include "Includes/Transparency.include"

uniform vec3 cameraPosition;

float noise(vec3 position, int octaves, float frequency, float persistence) {
    float total = 0.0; // Total value so far
    float maxAmplitude = 0.0; // Accumulates highest theoretical amplitude
    float amplitude = 1.0;
    for (int i = 0; i < octaves; i++) {

        // Get the noise sample
        total += snoise(position * frequency) * amplitude;

        // Make the wavelength twice as small
        frequency *= 2.0;

        // Add to our maximum possible amplitude
        maxAmplitude += amplitude;

        // Reduce amplitude according to persistence for the next octave
        amplitude *= persistence;
    }

    // Scale the result by the maximum amplitude
    return total / maxAmplitude;
}

float ridgedNoise(vec3 position, int octaves, float frequency, float persistence) {
    float total = 0.0; // Total value so far
    float maxAmplitude = 0.0; // Accumulates highest theoretical amplitude
    float amplitude = 1.0;
    for (int i = 0; i < octaves; i++) {

        // Get the noise sample
        total += ((1.0 - abs(snoise(position * frequency))) * 2.0 - 1.0) * amplitude;

        // Make the wavelength twice as small
        frequency *= 2.0;

        // Add to our maximum possible amplitude
        maxAmplitude += amplitude;

        // Reduce amplitude according to persistence for the next octave
        amplitude *= persistence;
    }

    // Scale the result by the maximum amplitude
    return total / maxAmplitude;
}

void main() {
    float inside = 1.6;
    float outside = 2.6;
    if(length(position_in_object_coordinates) > outside || length(position_in_object_coordinates) < inside) {
        discard;
    }

    // Simulate transparent shadows by using stochastic discard
    //const float stepInterval = 0.05;
    // discard;
    //if (mod(dot(vOutput.positionWorld, vec3(1)), stepInterval) > 0.5 * stepInterval ) discard;

    // Create a material to store the properties on
    //Material m = getDefaultMaterial();
    TransparentMaterial tm = getDefaultTransparentMaterial();

    vec2 newTexCoords = vOutput.texcoord;
    newTexCoords.x = (length(position_in_object_coordinates) - inside) / (outside - inside);
    // ^ adjust so inner ring edge is 0, outer edge is 1

    // Sample the diffuse color
    //vec4 sampledDiffuse = texture(p3d_Texture0, vOutput.texcoord);
    vec4 sampledDiffuse = texture(p3d_Texture0, newTexCoords);
    
    // Alpha test
    // if (sampledDiffuse.a < 0.5) discard;

    // Sample the other maps
    vec4 sampledNormal  = texture(p3d_Texture1, vOutput.texcoord);
    vec4 sampledSpecular = texture(p3d_Texture2, vOutput.texcoord);
    vec4 sampledRoughness = texture(p3d_Texture3, vOutput.texcoord);
        
    // Store the properties
    //m.baseColor = sampledDiffuse.rgb * vOutput.materialDiffuse.rgb;
    //m.roughness = sampledRoughness.r * roughnessFactor;
    //m.specular = sampledSpecular.r * specularFactor;
    //m.metallic = metallic;
    //m.normal = mixedNormal;
    //m.position = vOutput.positionWorld;
    //m.roughness = 0.4;
    //m.specular = 0.01;
    //m.metallic = 0.0;
    //m.translucency = (vOutput.materialDiffuse.r + vOutput.materialDiffuse.g + vOutput.materialDiffuse.b) / 3;
    //tm.color = sampledDiffuse.rgb * vOutput.materialDiffuse.rgb;
    tm.color = sampledDiffuse.rgb * vOutput.materialDiffuse.rgb;
    tm.alpha = (sampledDiffuse.r + sampledDiffuse.g + sampledDiffuse.b) * 3.0/ 3.0;
    tm.normal = normalize(vOutput.normalWorld);
    tm.roughness = vOutput.materialSpecular.z;
    tm.specular = vOutput.materialSpecular.x;
    tm.metallic = vOutput.materialSpecular.y;


    //noise//
    vec3 position = normalize(vOutput.normalWorld);

    float n1 = noise(position, 6, 10.0, 0.8);
    float n2 = ridgedNoise(position, 5, 5.8, 0.75) - 0.01;
    float n3 = snoise(position);
    float n = n1 + n2 + n3;
    tm.color = sampledDiffuse.rgb * vOutput.materialDiffuse.rgb * n;
    tm.color = vec3(n, n, 1.0);
    //end noise//


    // Write the material to the G-Buffer
    //renderMaterial(m);
    renderTransparentMaterial(tm);
}