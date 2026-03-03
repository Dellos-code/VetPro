package com.vetpro.controller;

import com.vetpro.model.Prescription;
import com.vetpro.service.PrescriptionService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/prescriptions")
public class PrescriptionController {

    private final PrescriptionService prescriptionService;

    public PrescriptionController(PrescriptionService prescriptionService) {
        this.prescriptionService = prescriptionService;
    }

    @PostMapping
    public ResponseEntity<Prescription> createPrescription(@Valid @RequestBody Prescription prescription) {
        Prescription created = prescriptionService.createPrescription(prescription);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Prescription> getPrescription(@PathVariable Long id) {
        return prescriptionService.getPrescriptionById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/record/{recordId}")
    public ResponseEntity<List<Prescription>> getByRecord(@PathVariable Long recordId) {
        return ResponseEntity.ok(prescriptionService.getPrescriptionsByRecord(recordId));
    }
}
