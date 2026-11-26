#version 460

uniform mat4 p3d_ProjectionMatrix; 
uniform mat4 p3d_ViewMatrix;

uniform vec3 camPos;
uniform float majorScale;
uniform float minorScale;

in vec3 nearPoint; 
in vec3 farPoint; 

out vec4 p3d_FragColor;

vec4 grid(vec3 fragPos3D, float scale, bool drawAxis)
{
    vec2 coord = fragPos3D.xy * scale;
    vec2 derivative = fwidth(coord);
    vec2 grid = abs(fract(coord - 0.5) - 0.5) / derivative;

    float line = min(grid.x, grid.y);
    
    float minimumy = min(derivative.y, 1);
    float minimumx = min(derivative.x, 1);
    
    vec4 color = vec4(0.2, 0.2, 0.2, 1.0 - min(line, 1.0));
    
    if(fragPos3D.x > -0.1 * minimumx && fragPos3D.x < 0.1 * minimumx)
        color.z = 1.0;
    if(fragPos3D.y > -0.1 * minimumy && fragPos3D.y < 0.1 * minimumy)
        color.x = 1.0;
        
    return color;
}

float computeDepth(vec3 pos)
{
    vec4 clip = p3d_ProjectionMatrix * p3d_ViewMatrix * vec4(pos, 1.0);
    float ndcDepth = clip.z / clip.w;
    return ndcDepth * 0.5 + 0.5;
}

float computeLinearDepth(vec3 pos)
{
    vec4 clip_space_pos = p3d_ProjectionMatrix * p3d_ViewMatrix * vec4(pos.xyz, 1.0);
    float clip_space_depth = (clip_space_pos.z + 1.0) / clip_space_pos.w;
    return 1.0 - smoothstep(-5, 5, clip_space_depth);
}

float computeGrazingFade(vec3 pos)
{
	vec3 viewDir = normalize(pos - camPos);
    // Grid plane is xy-plane, normal is (0,0,1)
    float NdotV = abs(dot(viewDir, vec3(0.0, 0.0, 1.0)));
    // When NdotV is small (looking at horizon), fade increases
    return smoothstep(0.02, 0.5, NdotV);
}

float computeHeightFade(float camHeight)
{
    // Fade in when very close to the ground (prevents shimmer when embedded)
    // Fade out as camera rises far above the grid (prevents aliasing/noise)
    float fadeIn  = smoothstep(0.0, 1.0, camHeight);
    float fadeOut = 1.0 - smoothstep(20.0, 120.0, camHeight);
    return fadeIn * fadeOut;
}

void main()
{    
    float t = -nearPoint.z / (farPoint.z - nearPoint.z);
	float valid = float(t >= 0 && t <= 1);
	
    vec3 fragPos3D = nearPoint + t * (farPoint - nearPoint);
    gl_FragDepth = computeDepth(fragPos3D);

    float fade = computeLinearDepth(fragPos3D);
    fade *= computeGrazingFade(fragPos3D);
    fade *= computeHeightFade(abs(camPos.z));

    p3d_FragColor = (grid(fragPos3D, majorScale, true) + grid(fragPos3D, minorScale, true)) * valid; 
    p3d_FragColor.a *= fade;
}
