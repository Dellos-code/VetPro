package com.vetpro.controller;

import com.vetpro.model.Appointment;
import com.vetpro.service.AppointmentService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/appointments")
public class AppointmentController {

    private final AppointmentService appointmentService;

    public AppointmentController(AppointmentService appointmentService) {
        this.appointmentService = appointmentService;
    }

    @PostMapping
    public ResponseEntity<Appointment> createAppointment(@Valid @RequestBody Appointment appointment) {
        Appointment created = appointmentService.createAppointment(appointment);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Appointment> getAppointment(@PathVariable Long id) {
        return appointmentService.getAppointmentById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/pet/{petId}")
    public ResponseEntity<List<Appointment>> getByPet(@PathVariable Long petId) {
        return ResponseEntity.ok(appointmentService.getAppointmentsByPet(petId));
    }

    @GetMapping("/vet/{vetId}")
    public ResponseEntity<List<Appointment>> getByVet(@PathVariable Long vetId) {
        return ResponseEntity.ok(appointmentService.getAppointmentsByVet(vetId));
    }

    @GetMapping("/range")
    public ResponseEntity<List<Appointment>> getByDateRange(
            @RequestParam LocalDateTime start,
            @RequestParam LocalDateTime end) {
        return ResponseEntity.ok(appointmentService.getAppointmentsByDateRange(start, end));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Appointment> updateAppointment(@PathVariable Long id,
                                                         @Valid @RequestBody Appointment appointment) {
        return appointmentService.getAppointmentById(id)
                .map(existing -> ResponseEntity.ok(appointmentService.updateAppointment(id, appointment)))
                .orElse(ResponseEntity.notFound().build());
    }

    @PutMapping("/{id}/cancel")
    public ResponseEntity<Appointment> cancelAppointment(@PathVariable Long id) {
        return ResponseEntity.ok(appointmentService.cancelAppointment(id));
    }

    @PutMapping("/{id}/complete")
    public ResponseEntity<Appointment> completeAppointment(@PathVariable Long id) {
        return ResponseEntity.ok(appointmentService.completeAppointment(id));
    }
}
