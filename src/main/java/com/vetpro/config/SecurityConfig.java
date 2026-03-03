package com.vetpro.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .httpBasic(Customizer.withDefaults())
            .headers(headers -> headers.frameOptions(frame -> frame.disable()))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/h2-console/**").permitAll()
                .requestMatchers(HttpMethod.POST, "/api/users/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/reports/**").hasAnyRole("ADMIN", "VET")
                .requestMatchers(HttpMethod.POST, "/api/prescriptions/**").hasRole("VET")
                .requestMatchers(HttpMethod.POST, "/api/medical-records/**").hasRole("VET")
                .requestMatchers(HttpMethod.POST, "/api/vaccine-records/**").hasRole("VET")
                .requestMatchers(HttpMethod.POST, "/api/hospitalizations/**").hasRole("VET")
                .requestMatchers(HttpMethod.PUT, "/api/hospitalizations/*/discharge").hasRole("VET")
                .requestMatchers(HttpMethod.POST, "/api/appointments/**").hasAnyRole("OWNER", "RECEPTIONIST", "VET", "ADMIN")
                .requestMatchers(HttpMethod.GET, "/api/medications/low-stock").hasAnyRole("ADMIN", "VET")
                .requestMatchers(HttpMethod.POST, "/api/medications/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.PUT, "/api/medications/**").hasAnyRole("ADMIN", "VET")
                .requestMatchers(HttpMethod.DELETE, "/api/users/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            );

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
