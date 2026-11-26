#version 460 

uniform mat4 p3d_ProjectionMatrixInverse; 
uniform mat4 p3d_ViewMatrixInverse;

in vec4 p3d_Vertex;

out vec3 nearPoint;
out vec3 farPoint;

vec3 UnprojectPoint(float x, float y, float z)
{
    vec4 clipCoords = vec4(x, y, z, 1.0);
    vec4 worldCoords = p3d_ViewMatrixInverse * p3d_ProjectionMatrixInverse * clipCoords;
    return worldCoords.xyz / worldCoords.w;
}

void main()
{
    gl_Position = vec4(p3d_Vertex.xyz, 1.0);
    nearPoint = UnprojectPoint(p3d_Vertex.x, p3d_Vertex.y, -1.0);
    farPoint = UnprojectPoint(p3d_Vertex.x, p3d_Vertex.y, 1.0);
}
