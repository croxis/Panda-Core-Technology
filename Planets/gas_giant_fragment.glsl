#version 410


#pragma include "Includes/Structures/VertexOutput.struct"
#pragma include "noise3D.glsl"

// Input from the vertex shader
layout(location=0) in VertexOutput vOutput;

// Texture Samplers
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
uniform sampler2D p3d_Texture2;
uniform sampler2D p3d_Texture3;

uniform float osg_FrameTime;

// This is required for the materials
#pragma include "Includes/MaterialPacking.include"
#pragma include "Includes/CommonFunctions.include"

// This include enables us to compute the tangent in the fragment shader
#pragma include "Includes/TangentFromDDX.include"

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

    // Create a material to store the properties on
    Material m = getDefaultMaterial();

    // Sample the diffuse color
    vec4 sampledDiffuse = texture(p3d_Texture0, vOutput.texcoord);
    
    // Alpha test
    // if (sampledDiffuse.a < 0.5) discard;

    // Sample the other maps
    vec4 sampledNormal  = texture(p3d_Texture1, vOutput.texcoord);
    vec4 sampledSpecular = texture(p3d_Texture2, vOutput.texcoord);
    vec4 sampledRoughness = texture(p3d_Texture3, vOutput.texcoord);
        
    // Extract the material properties 
    float bumpFactor = vOutput.materialDiffuse.w * 0.0;
    float specularFactor = vOutput.materialSpecular.x;
    float metallic = vOutput.materialSpecular.y;
    float roughnessFactor = vOutput.materialSpecular.z;

    // Merge the detail normal with the vertex normal
    vec3 detailNormal = sampledNormal.xyz * 2.0 - 1.0;
    vec3 tangent; vec3 binormal;
    reconstructTanBin(tangent, binormal);
    vec3 mixedNormal = mergeNormal(detailNormal, bumpFactor, vOutput.normalWorld, tangent, binormal);

    // Store the properties
    m.baseColor = sampledDiffuse.rgb * vOutput.materialDiffuse.rgb;
    m.roughness = sampledRoughness.r * roughnessFactor;
    m.specular = sampledSpecular.r * specularFactor;
    m.metallic = metallic;
    m.normal = mixedNormal;
    m.position = vOutput.positionWorld;
    // m.metallic = 0.0;

    //noise//
    // Use fNormal + time for evolution
    // reduce frametime for more natural time
    float time = osg_FrameTime / 100.0;
    vec3 position = mixedNormal + vec3(time, time, 0.0);

    float n1 = noise(position, 6, 10.0, 0.8) * 0.01;
    float n2 = ridgedNoise(position, 5, 5.8, 0.75) * 0.015 - 0.01;

    // Storm Threshold //
    // Get the three threshold samples
    float s = 0.6;
    float t1 = snoise(position * 2.0) - s;
    float t2 = snoise((position + 800.0) * 2.0) - s;
    float t3 = snoise((position + 1600.0) * 2.0) - s;
    // Intersect them and get rid of negatives
    float threshold = max(t1 * t2 * t3, 0.0);
    //m.baseColor.r += threshold * 3.0;//Debug
    // End Storm Threshold //

    float n3 = snoise(position * 0.1) * threshold;
    float n = n1 + n2 + n3;
    vec2 newTexCoord;
    newTexCoord.x = vOutput.texcoord.x + n;
    newTexCoord.y = 0;
    vec3 texColor = texture(p3d_Texture0, newTexCoord).rgb;
    m.baseColor = texColor;
    //end noise//


    // Write the material to the G-Buffer
    renderMaterial(m);
}