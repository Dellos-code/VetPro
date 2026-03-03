package com.vetpro.controller;

import com.vetpro.model.MedicalRecord;
import com.vetpro.service.MedicalRecordService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/medical-records")
public class MedicalRecordController {

    private final MedicalRecordService medicalRecordService;

    public MedicalRecordController(MedicalRecordService medicalRecordService) {
        this.medicalRecordService = medicalRecordService;
    }

    @PostMapping
    public ResponseEntity<MedicalRecord> createRecord(@Valid @RequestBody MedicalRecord record) {
        MedicalRecord created = medicalRecordService.createRecord(record);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/{id}")
    public ResponseEntity<MedicalRecord> getRecord(@PathVariable Long id) {
        return medicalRecordService.getRecordById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/pet/{petId}")
    public ResponseEntity<List<MedicalRecord>> getRecordsByPet(@PathVariable Long petId) {
        return ResponseEntity.ok(medicalRecordService.getRecordsByPet(petId));
    }

    @GetMapping("/vet/{vetId}")
    public ResponseEntity<List<MedicalRecord>> getRecordsByVet(@PathVariable Long vetId) {
        return ResponseEntity.ok(medicalRecordService.getRecordsByVet(vetId));
    }
}
