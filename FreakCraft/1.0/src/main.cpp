#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <iostream>
#include <vector>
const unsigned int screenwidth = 1280;
const unsigned int screenheight = 720;
const char *vertexshader = R"glsl(
#version 330 core
layout (location = 0) in vec3 apos;
layout (location = 1) in vec3 acolor;
layout (location = 2) in vec3 anormal;
out vec3 ourcolor;
out vec3 normal;
out vec3 fragpos;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main() {
    gl_Position = projection * view * model * vec4(apos, 1.0f);
    ourcolor = acolor;
    normal = mat3(transpose(inverse(model))) * anormal;
    fragpos = vec3(model * vec4(apos, 1.0f));
}
)glsl";
const char *fragmentshader = R"glsl(
#version 330 core
in vec3 ourcolor;
in vec3 normal;
in vec3 fragpos;
out vec4 fragcolor;
uniform vec3 lightpos;
uniform vec3 viewpos;
void main() {
    float ambientstrength = 0.2f;
    vec3 ambient = ambientstrength * vec3(1.0f);
    vec3 norm = normalize(normal);
    vec3 lightdir = normalize(lightpos - fragpos);
    float diff = max(dot(norm, lightdir), 0.0f);
    vec3 diffuse = diff * vec3(1.0f);
    float specularstrength = 0.5f;
    vec3 viewdir = normalize(viewpos - fragpos);
    vec3 reflectdir = reflect(-lightdir, norm);
    float spec = pow(max(dot(viewdir, reflectdir), 0.0f), 32);
    vec3 specular = specularstrength * spec * vec3(1.0f);
    vec3 result = (ambient + diffuse + specular) * ourcolor;
    fragcolor = vec4(result, 1.0f);
}
)glsl";
glm::vec3 camerapos(0.0f, 25.0f, 25.0f);
glm::vec3 camerafront(0.0f, -0.5f, -1.0f);
glm::vec3 cameraup(0.0f, 1.0f, 0.0f);
glm::vec3 lightpos(50.0f, 100.0f, 50.0f);
float lastx = screenwidth / 2.0f;
float lasty = screenheight / 2.0f;
float yaw = -90.0f;
float pitch = 0.0f;
float cameraspeed = 15.0f;
float sensitivity = 0.5f;
float deltatime = 0.0f;
float lastframe = 0.0f;
class Shader {
public:
    unsigned int id;
    Shader(const char *vertexsource, const char *fragmentsource) {
        unsigned int vertex = glCreateShader(GL_VERTEX_SHADER);
        glShaderSource(vertex, 1, &vertexsource, NULL);
        glCompileShader(vertex);
        unsigned int fragment = glCreateShader(GL_FRAGMENT_SHADER);
        glShaderSource(fragment, 1, &fragmentsource, NULL);
        glCompileShader(fragment);
        checkcompileerrors(fragment, "FRAGMENT");
        id = glCreateProgram();
        glAttachShader(id, vertex);
        glAttachShader(id, fragment);
        glLinkProgram(id);
        checkcompileerrors(id, "PROGRAM");
        glDeleteShader(vertex);
        glDeleteShader(fragment);
    }
    void use() {
        glUseProgram(id);
    }
    void setmat4(const std::string &name, const glm::mat4 &mat) const {
        glUniformMatrix4fv(glGetUniformLocation(id, name.c_str()), 1, GL_FALSE, &mat[0][0]);
    }
    void setvec3(const std::string &name, const glm::vec3 &value) const {
        glUniform3fv(glGetUniformLocation(id, name.c_str()), 1, &value[0]);
    }
private:
    void checkcompileerrors(unsigned int shader, std::string type) {
        int success;
        char infolog[1024];
        if (type != "PROGRAM") {
            glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
            if (!success) {
                glGetShaderInfoLog(shader, 1024, NULL, infolog);
                std::cout << "error shader compilation" << infolog << std::endl;
            }
        }
        else {
            glGetProgramiv(shader, GL_LINK_STATUS, &success);
            if (!success) {
                glGetShaderInfoLog(shader, 1024, NULL, infolog);
                std::cout << "error shader linking" << infolog << std::endl;
            }
        }
    }
};
class Chunk {
public:
    static const int size = 16;
    static const int height = 64;
    int chunkx, chunkz;
    unsigned char blocks[size][height][size];
    unsigned int vao, vbo;
    Chunk(int x, int z) : chunkx(x), chunkz(z) {
        generateterrain();
        createmesh();
    }
    void draw() {
        glBindVertexArray(vao);
        glDrawArrays(GL_TRIANGLES, 0, vertices.size() / 9);
    }
private:
    std::vector<float> vertices;
    void generateterrain() {
        for (int x = 0; x < size; x++) {
            for (int z = 0; z < size; z++) {
                int worldx = x + chunkx * size;
                int worldz = z + chunkz * size;
                float heightbase = 20.0f;
                float noise1 = sin(worldx * 0.1f) * 3.0f;
                float noise2 = cos(worldz * 0.1f) * 3.0f;
                float noise3 = sin(worldx * 0.05f + worldz * 0.05f) * 5.0f;
                float terrainheight = heightbase + noise1 + noise2 + noise3;
                terrainheight = glm::clamp(terrainheight, 1.0f, static_cast<float>(height - 5));
                for (int y = 0; y < height; y++) {
                    if (y < terrainheight - 8) blocks[x][y][z] = 3;
                    else if (y < terrainheight - 3) blocks[x][y][z] = 2;
                    else if (y < terrainheight) blocks[x][y][z] = 1;
                    else blocks[x][y][z] = 0;
                }
            }
        }
    }
    void addvertex(float x, float y, float z, glm::vec3 color, glm::vec3 normal) {
        vertices.insert(vertices.end(), {x, y, z});
        vertices.insert(vertices.end(), {color.r, color.g, color.b});
        vertices.insert(vertices.end(), {normal.x, normal.y, normal.z});
    }
    void addface(const glm::vec3 &position, const glm::vec3 &color, const glm::vec3 &normal) {
        const glm::vec3 &p = position;
        const float size = 1.0f;
        if (normal == glm::vec3(0, 1, 0)) {
            addvertex(p.x, p.y + size, p.z, color, normal);
            addvertex(p.x + size, p.y + size, p.z, color, normal);
            addvertex(p.x + size, p.y + size, p.z + size, color, normal);
            addvertex(p.x, p.y + size, p.z, color, normal);
            addvertex(p.x + size, p.y + size, p.z + size, color, normal);
            addvertex(p.x, p.y + size, p.z + size, color, normal);
        }
        else if (normal == glm::vec3(0, -1, 0)) {
            addvertex(p.x, p.y, p.z, color, normal);
            addvertex(p.x + size, p.y, p.z, color, normal);
            addvertex(p.x + size, p.y, p.z + size, color, normal);
            addvertex(p.x, p.y, p.z, color, normal);
            addvertex(p.x + size, p.y, p.z + size, color, normal);
            addvertex(p.x, p.y, p.z + size, color, normal);
        }
        else if (normal == glm::vec3(1, 0, 0)) {
            addvertex(p.x + size, p.y, p.z, color, normal);
            addvertex(p.x + size, p.y + size, p.z, color, normal);
            addvertex(p.x + size, p.y + size, p.z + size, color, normal);
            addvertex(p.x + size, p.y, p.z, color, normal);
            addvertex(p.x + size, p.y + size, p.z + size, color, normal);
            addvertex(p.x + size, p.y, p.z + size, color, normal);
        }
        else if (normal == glm::vec3(-1, 0, 0)) {
            addvertex(p.x, p.y, p.z, color, normal);
            addvertex(p.x, p.y + size, p.z, color, normal);
            addvertex(p.x, p.y + size, p.z + size, color, normal);
            addvertex(p.x, p.y, p.z, color, normal);
            addvertex(p.x, p.y + size, p.z + size, color, normal);
            addvertex(p.x, p.y, p.z + size, color, normal);
        }
        else if (normal == glm::vec3(0, 0, 1)) {
            addvertex(p.x, p.y, p.z + size, color, normal);
            addvertex(p.x + size, p.y, p.z + size, color, normal);
            addvertex(p.x + size, p.y + size, p.z + size, color, normal);
            addvertex(p.x, p.y, p.z + size, color, normal);
            addvertex(p.x + size, p.y + size, p.z + size, color, normal);
            addvertex(p.x, p.y + size, p.z + size, color, normal);
        }
        else if (normal == glm::vec3(0, 0, -1)) {
            addvertex(p.x, p.y, p.z, color, normal);
            addvertex(p.x + size, p.y, p.z, color, normal);
            addvertex(p.x + size, p.y + size, p.z, color, normal);
            addvertex(p.x, p.y, p.z, color, normal);
            addvertex(p.x + size, p.y + size, p.z, color, normal);
            addvertex(p.x, p.y + size, p.z, color, normal);
        }
    }
    void createmesh() {
        for (int x = 0; x < size; x++) {
            for (int y = 0; y < height; y++) {
                for (int z = 0; z < size; z++) {
                    if (blocks[x][y][z] == 0) continue;
                    glm::vec3 color;
                    switch (blocks[x][y][z]) {
                        case 1: color = glm::vec3(0.2f, 0.8f, 0.3f); break;
                        case 2: color = glm::vec3(0.5f, 0.4f, 0.3f); break;
                        case 3: color = glm::vec3(0.4f, 0.4f, 0.4f); break;
                    }
                    if (y == height - 1 || blocks[x][y + 1][z] == 0) addface(glm::vec3(x, y, z), color, glm::vec3(0, 1, 0));
                    if (y == 0 || blocks[x][y - 1][z] == 0) addface(glm::vec3(x, y, z), color, glm::vec3(0, -1, 0));
                    if (x == size - 1 || blocks[x + 1][y][z] == 0) addface(glm::vec3(x, y, z), color, glm::vec3(1, 0, 0));
                    if (x == 0 || blocks[x - 1][y][z] == 0) addface(glm::vec3(x, y, z), color, glm::vec3(-1, 0, 0));
                    if (z == size - 1 || blocks[x][y][z + 1] == 0) addface(glm::vec3(x, y, z), color, glm::vec3(0, 0, 1));
                    if (z == 0 || blocks[x][y][z - 1] == 0) addface(glm::vec3(x, y, z), color, glm::vec3(0, 0, -1));
                }
            }
        }
        glGenVertexArrays(1, &vao);
        glGenBuffers(1, &vbo);
        glBindVertexArray(vao);
        glBindBuffer(GL_ARRAY_BUFFER, vbo);
        glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), &vertices[0], GL_STATIC_DRAW);
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)0);
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(3 * sizeof(float)));
        glEnableVertexAttribArray(1);
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(6 * sizeof(float)));
        glEnableVertexAttribArray(2);
        glBindBuffer(GL_ARRAY_BUFFER, 0);
        glBindVertexArray(0);
    }
};
std::vector<Chunk> chunks;
void framebuffersizecallback(GLFWwindow *window, int width, int height) {
    glViewport(0, 0, width, height);
}
void processinput(GLFWwindow *window) {
    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
        glfwSetWindowShouldClose(window, true);
    }
    glm::vec3 frontflat = glm::normalize(glm::vec3(camerafront.x, 0.0f, camerafront.z));
    glm::vec3 rightflat = glm::normalize(glm::cross(frontflat, glm::vec3(0.0f, 1.0f, 0.0f)));
    float velocity = cameraspeed * deltatime;
    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS) {
        camerapos += frontflat * velocity;
    }
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS) {
        camerapos -= frontflat * velocity;
    }
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS) {
        camerapos += rightflat * velocity;
    }
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS) {
        camerapos -= rightflat * velocity;
    }
    if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS) {
        camerapos += glm::vec3(0.0f, 1.0f, 0.0f) * velocity;
    }
    if (glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS) {
        camerapos -= glm::vec3(0.0f, 1.0f, 0.0f) * velocity;
    }
}
void mousecallback(GLFWwindow *window, double posx, double posy) {
    float offsetx = posx - lastx;
    float offsety = lasty - posy;
    lastx = posx;
    lasty = posy;
    offsetx *= sensitivity;
    offsety *= sensitivity;
    yaw += offsetx;
    pitch += offsety;
    if (pitch > 89.0f) pitch = 89.0f;
    if (pitch < -89.0f) pitch = -89.0f;
    glm::vec3 front;
    front.x = cos(glm::radians(yaw)) * cos(glm::radians(pitch));
    front.y = sin(glm::radians(pitch));
    front.z = sin(glm::radians(yaw)) * cos(glm::radians(pitch));
    camerafront = glm::normalize(front);
}
int main() {
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    GLFWwindow *window = glfwCreateWindow(screenwidth, screenheight, "luxykraft1.0", NULL, NULL);
    glfwMakeContextCurrent(window);
    glfwSetCursorPos(window, screenwidth / 2.0f, screenheight / 2.0f);
    glfwSetFramebufferSizeCallback(window, framebuffersizecallback);
    glfwSetCursorPosCallback(window, mousecallback);
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
    glfwSwapInterval(1);
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        std::cout << "fail glad init" << std::endl;
        return -1;
    }
    Shader shader(vertexshader, fragmentshader);
    shader.use();
    shader.setvec3("lightpos", lightpos);
    shader.setvec3("viewpos", camerapos);
    const int renderdistance = 10;
    for (int x = -renderdistance; x <= renderdistance; x++) {
        for (int z = -renderdistance; z <= renderdistance; z++) {
            chunks.emplace_back(x, z);
        }
    }
    glEnable(GL_DEPTH_TEST);
    while (!glfwWindowShouldClose(window)) {
        float currentframe = glfwGetTime();
        deltatime = currentframe - lastframe;
        lastframe = currentframe;
        processinput(window);
        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glm::mat4 projection = glm::perspective(glm::radians(45.0f), (float)screenwidth / (float)screenheight, 0.1f, 1000.0f);
        glm::mat4 view = glm::lookAt(camerapos, camerapos + camerafront, cameraup);
        shader.use();
        shader.setmat4("projection", projection);
        shader.setmat4("view", view);
        shader.setvec3("viewpos", camerapos);
        for (auto &chunk : chunks) {
            glm::mat4 model = glm::translate(glm::mat4(1.0f), glm::vec3(chunk.chunkx * Chunk::size, 0.0f, chunk.chunkz * Chunk::size));
            shader.setmat4("model", model);
            chunk.draw();
        }
        glfwSwapBuffers(window);
        glfwPollEvents();
    }
    glfwTerminate();
    return 0;
}